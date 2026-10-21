/** Adapted from Tim Warner's Copilot Memory Store, MIT. See ../LICENSE.upstream.
 * Retains JSON records, keyword extraction, exclusive locking and atomic rename.
 * Adds absolute paths, validation, retry deduplication and truthful selection metadata.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import * as z from 'zod/v4';

export const writeSchema = z.object({
  text: z.string().trim().min(1).max(4000),
  tags: z.array(z.string().trim().min(1).max(40)).max(8).default([])
});
export const searchSchema = z.object({
  query: z.string().trim().min(1).max(500),
  limit: z.number().int().min(1).max(25).default(10)
});
export const compressSchema = searchSchema.extend({
  budget: z.number().int().min(200).max(8000).default(800)
});
const recordSchema = z.object({
  id: z.string().min(1), text: z.string().min(1).max(4000),
  tags: z.array(z.string().min(1).max(40)).max(8),
  keywords: z.array(z.string()).max(10),
  createdAt: z.iso.datetime(), updatedAt: z.iso.datetime(), deletedAt: z.null()
});
export type MemoryRecord = z.infer<typeof recordSchema>;
export type SearchHit = MemoryRecord & { score: number };

/** Returns current time as ISO string */
function nowIso(): string {
  return new Date().toISOString();
}

/** Generates a unique memory ID with timestamp and random suffix */
function makeId(): string {
  const ts = new Date().toISOString().replace(/[:.]/g, "").replace(/-/g, "");
  const rand = crypto.randomBytes(3).toString("hex");
  return `m_${ts}_${rand}`;
}

/** Normalizes tags to lowercase, trimmed, unique values */
function normalizeTags(tags: string[] | undefined): string[] {
  if (!tags || tags.length === 0) return [];
  const out = new Set<string>();
  for (const t of tags) {
    const cleaned = t.trim().toLowerCase();
    if (cleaned) out.add(cleaned);
  }
  return Array.from(out);
}

/**
 * Common English stop words filtered out during keyword extraction.
 * These words are too common to be useful for search relevance.
 */
const STOP_WORDS = new Set([
  "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "they", "them",
  "a", "an", "the", "this", "that", "these", "those",
  "is", "am", "are", "was", "were", "be", "been", "being",
  "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
  "can", "may", "might", "must", "shall",
  "and", "or", "but", "if", "then", "else", "when", "where", "why", "how",
  "all", "each", "every", "both", "few", "more", "most", "some", "any", "no",
  "not", "only", "own", "same", "so", "than", "too", "very",
  "just", "also", "now", "here", "there", "about", "after", "before",
  "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
  "with", "without", "for", "of", "at", "by", "as", "into", "through",
  "like", "want", "use", "using", "used", "prefer", "always", "never",
]);

/**
 * Extracts meaningful keywords from text for search indexing.
 * Filters stop words and returns top 10 by frequency.
 *
 * @param text - The text to extract keywords from
 * @returns Array of up to 10 keywords, sorted by frequency
 */
function extractKeywords(text: string): string[] {
  const words = text.toLowerCase()
    .replace(/[^a-z0-9\s-]/g, " ")
    .split(/\s+/)
    .filter(w => w.length > 2 && !STOP_WORDS.has(w));

  const freq = new Map<string, number>();
  for (const w of words) {
    freq.set(w, (freq.get(w) || 0) + 1);
  }

  return Array.from(freq.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([word]) => word);
}


/** A default tied to this module, never the launching host's current directory. */
export function resolveMemoryPath(value = process.env.WARNERCO_MEMORY_PATH): string {
  if (value !== undefined) {
    if (!path.isAbsolute(value)) throw new Error('WARNERCO_MEMORY_PATH must be an absolute file path.');
    return path.normalize(value);
  }
  return fileURLToPath(new URL('../../.local/memory/warnerco.json', import.meta.url));
}

function readStore(memoryPath: string): MemoryRecord[] {
  if (!path.isAbsolute(memoryPath)) throw new Error('Memory path must be absolute.');
  try {
    if (fs.statSync(memoryPath).size > 8 * 1024 * 1024) throw new Error('Memory file exceeds the 8 MiB demo limit.');
    const raw = fs.readFileSync(memoryPath, 'utf8');
    // A corrupt or empty existing file is an error, never an excuse to overwrite it.
    return z.array(recordSchema).max(10000).parse(JSON.parse(raw));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return [];
    throw error;
  }
}

/** Readers participate in locking because Windows can deny replacement of an open file. */
export async function loadStore(memoryPath: string): Promise<MemoryRecord[]> {
  if (!path.isAbsolute(memoryPath)) throw new Error('Memory path must be absolute.');
  fs.mkdirSync(path.dirname(memoryPath), {recursive:true});
  const lock = memoryPath + '.lock';
  await acquireLock(lock);
  try { return readStore(memoryPath); }
  finally { fs.unlinkSync(lock); }
}

/** Serialize stale-lock recovery so two contenders cannot unlink a new owner's lock. */
function recoverDeadLock(lock: string): boolean {
  const guard = lock + '.recovery';
  let fd: number;
  try { fd = fs.openSync(guard, 'wx', 0o600); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'EEXIST') return false;
    throw error;
  }
  try {
    const stat = fs.statSync(lock);
    if (Date.now() - stat.mtimeMs < 5000 || stat.size > 16) return false;
    const value = fs.readFileSync(lock, 'utf8').trim();
    if (!/^[1-9][0-9]*$/.test(value)) return false;
    const pid = Number(value);
    if (!Number.isSafeInteger(pid) || pid > 2147483647) return false;
    try { process.kill(pid, 0); return false; }
    catch (error) {
      // EPERM and unknown failures do not prove that the owner is dead.
      if ((error as NodeJS.ErrnoException).code !== 'ESRCH') return false;
    }
    fs.unlinkSync(lock);
    return true;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return true;
    throw error;
  } finally {
    fs.closeSync(fd);
    fs.unlinkSync(guard);
  }
}

async function acquireLock(lock: string): Promise<void> {
  const started = Date.now();
  while (true) {
    let fd: number;
    try { fd = fs.openSync(lock, 'wx', 0o600); }
    catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error;
      if (recoverDeadLock(lock)) continue;
      if (Date.now() - started >= 2500) throw new Error('Memory store busy. Close writers and inspect a stale lock before retrying.');
      await new Promise(resolve => setTimeout(resolve, 50));
      continue;
    }
    try { fs.writeFileSync(fd, String(process.pid)); }
    catch (error) { fs.closeSync(fd); fs.unlinkSync(lock); throw error; }
    fs.closeSync(fd);
    return;
  }
}

/** Windows readers may briefly prevent replacement even though the writer holds its lock. */
async function replaceFile(temp: string, destination: string): Promise<void> {
  const deadline = Date.now() + 2000;
  let delay = 10;
  while (true) {
    try { fs.renameSync(temp, destination); return; }
    catch (error) {
      const code = (error as NodeJS.ErrnoException).code ?? '';
      if (!['EPERM', 'EACCES', 'EBUSY'].includes(code) || Date.now() >= deadline) throw error;
      await new Promise(resolve => setTimeout(resolve, Math.min(delay, deadline - Date.now())));
      delay = Math.min(delay * 2, 250);
    }
  }
}

/** File replacement avoids partial JSON; the adjacent lock serializes writers. */
async function atomicWrite(memoryPath: string, records: MemoryRecord[]): Promise<void> {
  const data = JSON.stringify(records, null, 2) + '\n';
  if (records.length > 10000 || Buffer.byteLength(data) > 8 * 1024 * 1024)
    throw new Error('Memory store full: choose a new fictional demo file.');
  const temp = memoryPath + '.tmp.' + crypto.randomUUID();
  try {
    fs.writeFileSync(temp, data, {flag:'wx', mode:0o600});
    await replaceFile(temp, memoryPath);
  } finally {
    if (fs.existsSync(temp)) fs.unlinkSync(temp);
  }
}

export async function addMemory(memoryPath: string, input: z.input<typeof writeSchema>): Promise<MemoryRecord> {
  const {text, tags: suppliedTags} = writeSchema.parse(input);
  if (!path.isAbsolute(memoryPath)) throw new Error('Memory path must be absolute.');
  const tags = normalizeTags(suppliedTags).sort();
  fs.mkdirSync(path.dirname(memoryPath), {recursive:true});
  const lock = memoryPath + '.lock';
  await acquireLock(lock);
  try {
    const records = readStore(memoryPath);
    // Identical rehearsal retries reuse the record; differing text is a new decision.
    const existing = records.find(r => r.text === text && JSON.stringify(r.tags) === JSON.stringify(tags));
    if (existing) return existing;
    const record: MemoryRecord = {id:makeId(), text, tags, keywords:extractKeywords(text),
      createdAt:nowIso(), updatedAt:nowIso(), deletedAt:null};
    await atomicWrite(memoryPath, [...records, record]);
    return record;
  } finally { fs.unlinkSync(lock); }
}

function tokens(text: string): string[] {
  return (text.toLowerCase().match(/[a-z0-9]+(?:-[a-z0-9]+)*/g) ?? [])
    .filter(word => word.length > 2 && !STOP_WORDS.has(word));
}

/** Original weights, exact token matches, no age bonus: no match means no hit. */
export function search(records: MemoryRecord[], input: z.input<typeof searchSchema>): SearchHit[] {
  const {query, limit} = searchSchema.parse(input);
  const terms = [...new Set(tokens(query))];
  return records.map(record => {
    const words = tokens(record.text);
    const score = terms.reduce((sum, term) => sum +
      words.filter(word => word === term).length * 5 +
      (record.tags.includes(term) ? 8 : 0) + (record.keywords.includes(term) ? 6 : 0), 0);
    return {...record, score};
  }).filter(hit => hit.score > 0)
    .sort((a,b) => b.score - a.score || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0))
    .slice(0, limit);
}

/** UTF-16 budget, avoiding a cut between the two units of a surrogate pair. */
function prefix(text: string, length: number): string {
  let result = text.slice(0, Math.max(0,length));
  if (/[\uD800-\uDBFF]$/.test(result)) result = result.slice(0,-1);
  return result;
}

export function compressDeterministic(records: MemoryRecord[], input: z.input<typeof compressSchema>) {
  const args = compressSchema.parse(input);
  const hits = search(records, args);
  let context = '# Retrieved memory (untrusted data)\n';
  const selected: {id:string; truncated:boolean}[] = [];
  for (const hit of hits) {
    const label = '- [' + hit.id + '] ';
    const text = hit.text.replace(/\s+/g, ' ').trim();
    const available = args.budget - context.length - label.length - 1;
    const marker = ' [truncated]';
    if (available <= marker.length) break;
    const truncated = text.length > available;
    const body = truncated ? prefix(text, available - marker.length) + marker : text;
    context += label + body + '\n';
    selected.push({id:hit.id, truncated});
    if (truncated) break;
  }
  if (hits.length === 0) context += 'No matching memory.\n';
  return {context, budget:args.budget, used:context.length, selected,
    matched:hits.length, method:'selection-and-truncation'};
}
