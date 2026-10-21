import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {once} from 'node:events';
import {fileURLToPath} from 'node:url';
const server=fileURLToPath(new URL('../dist/server.js',import.meta.url));
const meta={'io.modelcontextprotocol/protocolVersion':'2026-07-28',
  'io.modelcontextprotocol/clientCapabilities':{},
  'io.modelcontextprotocol/clientInfo':{name:'memory-check',version:'1.0'}};
export function connect(memoryPath,cwd) {
  const child=spawn(process.execPath,[server],{
    cwd, env:{...process.env,WARNERCO_MEMORY_PATH:memoryPath}, stdio:['pipe','pipe','pipe']
  });
  const pending=new Map(); let id=0; let diagnostics='';
  child.stderr.on('data',chunk=>{diagnostics+=chunk.toString();});
  createInterface({input:child.stdout}).on('line',line=>{
    let response;
    try { response=JSON.parse(line); }
    catch { for(const waiter of pending.values()) waiter.reject(new Error('Non-JSON stdout')); return; }
    const waiter=pending.get(response.id);
    if(waiter){clearTimeout(waiter.timer);pending.delete(response.id);waiter.resolve(response);}
  });
  child.on('error',error=>{for(const waiter of pending.values()) waiter.reject(error);});
  child.on('exit',()=>{for(const waiter of pending.values()) waiter.reject(new Error('Server exited: '+diagnostics));});
  return {
    call(method,params={}) {
      const callId=++id;
      return new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>{pending.delete(callId);reject(new Error('RPC timeout: '+method));},10000);
        pending.set(callId,{resolve,reject,timer});
        child.stdin.write(JSON.stringify({jsonrpc:'2.0',id:callId,method,params:{...params,_meta:meta}})+'\n');
      });
    },
    async close() {
      for(const waiter of pending.values()){clearTimeout(waiter.timer);waiter.reject(new Error('Client closed'));}
      pending.clear();
      if(child.exitCode!==null) return;
      const exited=once(child,'exit');
      child.stdin.end();
      const timer=setTimeout(()=>child.kill(),2000);
      try {await exited;} finally {clearTimeout(timer);}
    }
  };
}
