import {fork,spawn} from 'node:child_process';
import {once} from 'node:events';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {addMemory,loadStore,search,compressDeterministic,resolveMemoryPath} from '../dist/memoryStore.js';
import {connect} from './harness.mjs';

async function fixture(t) {
  const dir=await fs.mkdtemp(path.join(os.tmpdir(),'warnerco-memory-'));
  t.after(()=>fs.rm(dir,{recursive:true,force:true}));
  return {dir,file:path.join(dir,'nested','memory.json')};
}
const call=(client,name,args)=>client.call('tools/call',{name,arguments:args});
const data=response=>{
  assert.ok(!response.error,JSON.stringify(response));
  assert.ok(!response.result.isError,JSON.stringify(response));
  return response.result.structuredContent;
};

test('absolute default is module-relative; relative overrides fail',()=>{
  assert.equal(resolveMemoryPath(),fileURLToPath(new URL('../../.local/memory/warnerco.json',import.meta.url)));
  assert.throws(()=>resolveMemoryPath('relative.json'),/absolute/);
});
test('relevance excludes recent unrelated notes and stop-word-only queries',async t=>{
  const {file}=await fixture(t);
  await addMemory(file,{text:'INC-1042 Order API decision: compare failing instances.',tags:['Decision']});
  await addMemory(file,{text:'Fictional cafeteria menu: waffles.'});
  const records=await loadStore(file);
  assert.equal(search(records,{query:'INC-1042'}).length,1);
  assert.deepEqual(search(records,{query:'unicorns'}),[]);
  assert.deepEqual(search(records,{query:'the and'}),[]);
  assert.equal(search(records,{query:'decision'})[0].tags[0],'decision');
});
test('compression obeys every supported budget and reports only included records',async t=>{
  const {file}=await fixture(t);
  await addMemory(file,{text:'INC-1042 '+('check telemetry carefully 😀 '.repeat(100)),tags:['decision']});
  await addMemory(file,{text:'INC-1042 second observation.'});
  const records=await loadStore(file);
  for(let budget=200;budget<=8000;budget++){
    const result=compressDeterministic(records,{query:'INC-1042',budget});
    assert.equal(result.used,result.context.length);
    assert.ok(result.used<=budget);
    assert.ok(result.context.isWellFormed());
    for(const item of result.selected) assert.ok(result.context.includes(item.id));
    if(result.selected.some(item=>item.truncated)) assert.ok(result.context.includes('[truncated]'));
    if(budget===200) assert.equal(result.selected.length,1);
  }
  assert.throws(()=>compressDeterministic(records,{query:'INC-1042',budget:199}));
  assert.throws(()=>compressDeterministic(records,{query:'INC-1042',budget:200.5}));
});
test('corrupt storage and held locks fail without destroying data',async t=>{
  const {dir,file}=await fixture(t);
  await fs.mkdir(path.dirname(file),{recursive:true});
  await fs.writeFile(file,'BROKEN');
  await assert.rejects(addMemory(file,{text:'Do not overwrite.'}));
  assert.equal(await fs.readFile(file,'utf8'),'BROKEN');
  await fs.writeFile(file,'[]');
  await fs.writeFile(file+'.lock','test owner');
  await assert.rejects(addMemory(file,{text:'Do not steal lock.'}),/busy/);
  assert.equal(await fs.readFile(file,'utf8'),'[]');
  assert.equal(await fs.readFile(file+'.lock','utf8'),'test owner');
  assert.ok(dir);
});
test('stdio discovery, independent processes, concurrent writes and failure behavior',async t=>{
  const {dir,file}=await fixture(t);
  let first=connect(file,dir);
  try {
    assert.ok(!(await first.call('server/discover')).error);
    const tools=(await first.call('tools/list')).result.tools;
    assert.deepEqual(tools.map(tool=>tool.name).sort(),['memory_compress','memory_search','memory_write']);
    var saved=data(await call(first,'memory_write',{text:'INC-1042: request approval before rollback.',tags:['Decision','decision']}));
    const retry=data(await call(first,'memory_write',{text:'INC-1042: request approval before rollback.',tags:['decision']}));
    assert.equal(retry.memory.id,saved.memory.id);
    const invalid=await call(first,'memory_write',{text:'   '});
    assert.ok(invalid.error || invalid.result?.isError);
    const badBudget=await call(first,'memory_compress',{query:'INC-1042',budget:-1});
    assert.ok(badBudget.error || badBudget.result?.isError);
  } finally {await first.close();}
  const second=connect(file,path.dirname(dir)); const third=connect(file,dir);
  try {
    const hits=data(await call(second,'memory_search',{query:'INC-1042'})).hits;
    assert.equal(hits[0].id,saved.memory.id);
    assert.equal(data(await call(second,'memory_search',{query:'MISSING-9876'})).hits.length,0);
    const compact=data(await call(second,'memory_compress',{query:'INC-1042',budget:250}));
    assert.ok(compact.context.includes('approval before rollback'));
    assert.ok(compact.used<=250);
    const results=await Promise.all(Array.from({length:8},(_,i)=>
      call(i%2 ? second : third,'memory_write',{text:'INC-1042 concurrent observation '+i})));
    results.forEach(data);
    assert.equal((await loadStore(file)).length,9);
    await fs.writeFile(file,'{}');
    const corrupt=await call(second,'memory_search',{query:'INC-1042'});
    assert.equal(corrupt.result.isError,true);
    assert.equal(await fs.readFile(file,'utf8'),'{}');
  } finally {await second.close();await third.close();}
});

test('dead old owners recover safely while live and recent locks stay protected',async t=>{
  const {file}=await fixture(t);
  await fs.mkdir(path.dirname(file),{recursive:true});
  await fs.writeFile(file,'[]');
  const owner=spawn(process.execPath,['-e','']);
  await once(owner,'exit');
  const old=new Date(Date.now()-10000);
  await fs.writeFile(file+'.lock',String(process.pid));
  await fs.utimes(file+'.lock',old,old);
  await assert.rejects(addMemory(file,{text:'Live owner must keep its lock.'}),/busy/);
  assert.equal(await fs.readFile(file+'.lock','utf8'),String(process.pid));
  await fs.writeFile(file+'.lock',String(owner.pid));
  await assert.rejects(addMemory(file,{text:'Recent dead lock is still protected.'}),/busy/);
  await fs.utimes(file+'.lock',old,old);
  const writers=Array.from({length:4},(_,i)=>startWorker('writer',file,'recovery-'+i,1));
  t.after(()=>writers.forEach(w=>w.child.kill()));
  await Promise.all(writers.map(w=>w.done));
  assert.equal((await loadStore(file)).length,4);
  await assert.rejects(fs.stat(file+'.lock'),{code:'ENOENT'});
  await assert.rejects(fs.stat(file+'.lock.recovery'),{code:'ENOENT'});
});

function startWorker(mode,file,label='',count=0) {
  const child=fork(new URL('./io-worker.mjs',import.meta.url),[mode,file,label,String(count)],
    {stdio:['ignore','ignore','pipe','ipc']});
  let diagnostics='',result;
  child.stderr.on('data',chunk=>{diagnostics+=chunk;});
  let readyResolve,readyReject;
  const ready=new Promise((resolve,reject)=>{readyResolve=resolve;readyReject=reject;});
  // Writers do not send readiness; avoid an unhandled rejection for unused readiness.
  ready.catch(()=>{});
  child.on('message',message=>{if(message.ready) readyResolve();else result=message;});
  const done=new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{child.kill();reject(new Error('Worker timeout'));},20000);
    child.once('error',error=>{clearTimeout(timer);readyReject(error);reject(error);});
    child.once('exit',code=>{
      clearTimeout(timer);
      if(code===0) resolve(result);
      else {const error=new Error('Worker failed: '+diagnostics);readyReject(error);reject(error);}
    });
  });
  // Cleanup remains the test's responsibility even when readiness fails.
  done.catch(()=>{});
  return {child,ready,done,stop(){if(child.connected) child.send('stop');}};
}

test('four writers retain every record while three independent readers loop',async t=>{
  const {file}=await fixture(t);
  await addMemory(file,{text:'INC-1042 seed.'});
  const readers=Array.from({length:3},()=>startWorker('reader',file));
  const writers=[];
  t.after(()=>[...readers,...writers].forEach(w=>w.child.kill()));
  await Promise.all(readers.map(r=>r.ready));
  try {
    writers.push(...Array.from({length:4},(_,i)=>startWorker('writer',file,'writer-'+i,25)));
    const results=await Promise.all(writers.map(w=>w.done));
    assert.equal(results.reduce((sum,r)=>sum+r.written,0),100);
  } finally {readers.forEach(r=>r.stop());}
  const reads=await Promise.all(readers.map(r=>r.done));
  assert.ok(reads.every(r=>r.reads>0));
  const records=await loadStore(file);
  assert.equal(records.length,101);
  assert.equal(new Set(records.map(r=>r.text)).size,101);
});
