/** Exactly three stdio tools. No model, cloud credential or extra capability. */
import { McpServer } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { addMemory, loadStore, search, compressDeterministic,
  resolveMemoryPath, writeSchema, searchSchema, compressSchema } from './memoryStore.js';

const memoryPath = resolveMemoryPath();
const readonly = {readOnlyHint:true, destructiveHint:false, idempotentHint:true, openWorldHint:false};
const result = (data: Record<string, unknown>) => ({
  content:[{type:'text' as const, text:JSON.stringify(data)}], structuredContent:data
});
/** Convert storage failures into explicit tool errors; never fabricate empty success. */
async function guarded(action: () => Record<string, unknown> | Promise<Record<string, unknown>>) {
  try { return result(await action()); }
  catch (error) {
    console.error('Memory operation failed:', error);
    return {isError:true, content:[{type:'text' as const,
      text:'Memory operation failed. Check the server diagnostics; existing data was not reset.'}]};
  }
}
function createServer(): McpServer {
  const server = new McpServer({name:'warnerco-memory',version:'1.0.0'});
  server.registerTool('memory_write', {
    description:'Persist a fictional WARNERCO project memory. Identical text and normalized tags reuse the record.',
    inputSchema:writeSchema,
    annotations:{...readonly, readOnlyHint:false}
  }, args => guarded(async () => ({memory:await addMemory(memoryPath,args)})));
  server.registerTool('memory_search', {
    description:'Search stored memories by deterministic keyword relevance. Unmatched queries return no hits.',
    inputSchema:searchSchema, annotations:readonly
  }, args => guarded(() => ({hits:search(loadStore(memoryPath),args)})));
  server.registerTool('memory_compress', {
    description:'Select and truncate relevant memory into a context field within a UTF-16 character budget. Not semantic summarization. The host must explicitly use the context.',
    inputSchema:compressSchema, annotations:readonly
  }, args => guarded(() => compressDeterministic(loadStore(memoryPath),args)));
  return server;
}
try {
  serveStdio(createServer, {onerror:error => console.error(error)});
  console.error('WARNERCO memory server listening on stdio');
} catch (error) { console.error(error); process.exitCode=1; }
