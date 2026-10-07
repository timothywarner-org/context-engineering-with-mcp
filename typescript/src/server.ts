/** WARNERCO incident example using the official TypeScript MCP SDK.
 * Keep the same inputs and business results as the Python starter so language choice
 * does not change the lesson. Every incident is a fictional teaching fixture.
 */
import { McpServer } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import * as z from 'zod/v4';

/** Let the official entry point select the protocol era for the connecting client. */
function createServer(): McpServer {
  const server = new McpServer({name: 'warnerco-incidents', version: '1.0.0'});
  const incident = {id: 'INC-1042', owner: 'Priya Patel', service: 'Order API', status: 'Investigating', symptom: 'Timeouts after a deployment'};

  server.registerTool('get_incident', {
    description: 'Look up a WARNERCO incident by ID. This operation is read-only.',
    inputSchema: z.object({incident_id: z.string()})
  }, async ({incident_id}) => {
    // An explicit tool error prevents a missing record from masquerading as evidence.
    const key = incident_id.trim().toUpperCase();
    if (key !== incident.id) return {isError: true, content: [{type: 'text' as const, text: `Unknown incident: ${key}`} ]};
    return {content: [{type: 'text' as const, text: JSON.stringify(incident)}], structuredContent: incident};
  });
  server.registerResource('order-api-runbook', 'warnerco://runbooks/order-api', {
    description: 'The approved investigation procedure as URI-addressed context.', mimeType: 'text/plain'
  }, async uri => ({contents: [{uri: uri.href, text: 'Confirm the deployment time; inspect request failures; compare healthy and failing instances; request approval before rollback.'}]}));
  server.registerPrompt('investigate_incident', {
    description: 'Prepare an evidence-first investigation request for the user to invoke.',
    argsSchema: z.object({incident_id: z.string().default('INC-1042')})
  }, ({incident_id}) => ({messages: [{role: 'user' as const, content: {type: 'text' as const, text: `Investigate ${incident_id}. Read the incident and order-api runbook. Separate observed facts from hypotheses. Recommend the next check; request approval before changes.`}}]}));
  return server;
}

// This entry supports current discovery and older clients without a custom dispatcher.
try {
  serveStdio(createServer, {onerror: error => console.error(error)});
  console.error('WARNERCO incident server listening on stdio');
} catch (error) {
  console.error(error);
  process.exitCode = 1;
}
