import {addMemory,loadStore} from '../dist/memoryStore.js';
const [mode,file,label,countText]=process.argv.slice(2);
let stopping=false;
process.on('message',message=>{if(message==='stop') stopping=true;});
try {
  if(mode==='reader') {
    let reads=0;
    await loadStore(file);
    process.send?.({ready:true});
    while(!stopping) {
      await loadStore(file);
      reads++;
      await new Promise(resolve=>setImmediate(resolve));
    }
    process.send?.({reads});
  } else {
    for(let i=0;i<Number(countText);i++) await addMemory(file,{text:'INC-1042 '+label+' observation '+i});
    process.send?.({written:Number(countText)});
  }
  process.disconnect?.();
} catch(error) {
  console.error(error);
  process.exitCode=1;
  process.disconnect?.();
}
