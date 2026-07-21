#!/usr/bin/env node
// comms-coach Layer 1 — deterministic linguistic trend engine.
// Reads THIS project's Claude Code session transcripts, extracts only genuine
// human turns, computes linguistic metrics, classifies voice-likely turns, and
// buckets by week/month. Zero model calls. No external deps (pure fs + JSON).
//
// Usage:
//   node analyze.mjs [--project <path>] [--since YYYY-MM-DD] [--out <dir>]
// Defaults: project = process.cwd(); out = <project>/.claude/analysis
//
// Outputs (in --out):
//   comms-coach-metrics-<date>.json   full per-bucket + overall metrics
//   comms-coach-sample-<date>.json    ~25 most-recent voice-likely cleaned turns (Layer 2 input)
// Appends one line to <skillDir>/runs.jsonl and prints a summary to stdout.

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

// ---------- args ----------
const argv = process.argv.slice(2);
const getArg = (name, dflt) => {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt;
};
const projectArg = path.resolve(getArg('--project', process.cwd()));
const since = getArg('--since', null); // ISO date string; turns before are dropped
const outDir = path.resolve(getArg('--out', path.join(projectArg, '.claude', 'analysis')));
const skillDir = path.dirname(fileURLToPath(import.meta.url)); // cross-platform (handles Win drive + URL-encoding)
const today = new Date().toISOString().slice(0, 10);

const norm = (p) => (p || '').toLowerCase().replace(/\\/g, '/').replace(/\/+$/, '');
const targetCwd = norm(projectArg);

// ---------- discovery: this project's transcript dir, matched by `cwd` ----------
const projectsRoot = path.join(os.homedir(), '.claude', 'projects');
if (!fs.existsSync(projectsRoot)) {
  console.error(`No transcripts root at ${projectsRoot}`);
  process.exit(1);
}
const sessionFiles = [];
for (const dir of fs.readdirSync(projectsRoot, { withFileTypes: true })) {
  if (!dir.isDirectory()) continue;
  const dirPath = path.join(projectsRoot, dir.name);
  const jsonls = fs.readdirSync(dirPath).filter((f) => f.endsWith('.jsonl')); // top-level only; skips subagents/
  if (!jsonls.length) continue;
  // peek the first parseable line of the first file to read its cwd
  let dirCwd = null;
  outer: for (const f of jsonls) {
    const head = fs.readFileSync(path.join(dirPath, f), 'utf8').split('\n');
    for (const line of head) {
      if (!line.trim()) continue;
      try { const o = JSON.parse(line); if (o.cwd) { dirCwd = o.cwd; break outer; } } catch { /* skip */ }
    }
  }
  if (dirCwd && norm(dirCwd) === targetCwd) {
    for (const f of jsonls) sessionFiles.push(path.join(dirPath, f));
  }
}
if (!sessionFiles.length) {
  console.error(`No session transcripts matched project cwd: ${projectArg}`);
  console.error(`(searched ${projectsRoot})`);
  process.exit(1);
}

// ---------- text cleaning ----------
function clean(t) {
  if (!t) return '';
  t = t.replace(/<system-reminder>[\s\S]*?<\/system-reminder>/g, ' ');
  t = t.replace(/<ide_selection>[\s\S]*?<\/ide_selection>/g, ' ');
  t = t.replace(/<ide_opened_file>[\s\S]*?<\/ide_opened_file>/g, ' ');
  t = t.replace(/<task-notification>[\s\S]*?<\/task-notification>/g, ' ');
  t = t.replace(/<command-(?:name|message|args)>[\s\S]*?<\/command-(?:name|message|args)>/g, ' ');
  t = t.replace(/<local-command-[\s\S]*?<\/local-command-[a-z]+>/g, ' ');
  return t.replace(/\s+/g, ' ').trim();
}

// ---------- genuine-human-turn predicate ----------
function extractTurn(o) {
  if (o.type !== 'user') return null;
  if (o.isSidechain === true) return null;
  if (o.isMeta === true || o.isCompactSummary === true) return null; // defensive (not seen in this corpus)
  const content = o.message?.content;
  let raw = '';
  if (typeof content === 'string') {
    raw = content;
  } else if (Array.isArray(content)) {
    // A genuine human turn carries text block(s) and NO tool_result block.
    // (parentUuid is NOT a discriminator — only the session's first turn is null; every follow-up has a parent.)
    if (content.some((b) => b?.type === 'tool_result')) return null;
    raw = content.filter((b) => b?.type === 'text').map((b) => b.text || '').join('\n');
  } else return null;
  if (/^\s*<command-/.test(raw)) return null;
  const text = clean(raw);
  if (!text) return null;
  // Harness-injected payloads arrive as user-role text turns but are NOT human speech — drop them:
  //  • skill/command bodies (prefixed "Base directory for this skill:")
  //  • context-compaction summaries (auto-generated; ~2k words each, dominate avg_words/TTR)
  // (Both are fat Pattern-37 contaminants that otherwise leak into the voice-likely set.)
  if (/^Base directory for this skill:/i.test(text)) return null;
  if (/^This session is being continued from a previous conversation/i.test(text)) return null;
  return { ts: o.timestamp || null, text, sessionId: o.sessionId || null };
}

// ---------- metrics ----------
const countMatches = (s, re) => (s.match(re) || []).length;
function metrics(text) {
  const lower = text.toLowerCase();
  const words = lower.match(/[a-z']+/g) || [];
  const wc = words.length;
  const sentences = text.split(/[.!?]+/).map((s) => s.trim()).filter(Boolean);
  const sc = Math.max(sentences.length, 1);
  // "like" as discourse filler ONLY — subtract the common lexical uses (feel/look/would like, more like, like that…)
  const likeAll = countMatches(lower, /\blike\b/g);
  const likeLexical =
    countMatches(lower, /\b(?:feel|feels|felt|look|looks|looked|looking|seem|seems|seemed|sound|sounds|sounded|would|more|less|just|much|something|anything|nothing|someone|anyone)\s+like\b/g) +
    countMatches(lower, /(?:'d|i'd|we'd|they'd)\s+like\b/g) +
    countMatches(lower, /\blike\s+(?:to|that|this|these|those|a|an|the)\b/g);
  const fillerLike = Math.max(0, likeAll - likeLexical);
  const filler =
    countMatches(lower, /\bum\b|\buh\b|\byou know\b|\bkind of\b|\bsort of\b|\bi mean\b|\bbasically\b/g) +
    fillerLike;
  const tagQ =
    countMatches(lower, /\bright\?/g) + countMatches(lower, /makes? sense/g) + countMatches(lower, /you know\?/g);
  const hedge = countMatches(
    lower,
    /\bi feel like\b|\bi guess\b|\bi think\b|\bgut feeling\b|\bmaybe\b|\bprobably\b|\bi'm not sure\b/g,
  );
  const selfcorr =
    countMatches(lower, /(?:^|[,;:]\s*)actually\b|\bactually,|\bi mean\b/g) + // discourse "actually", not lexical
    countMatches(text, /\.\.\.|…/g) +
    countMatches(lower, /\bnot\b[^.?!]{1,40}\bbut\b/g);
  const directive =
    countMatches(lower, /\bi want\b|\bmake sure\b|\blet's\b|\bneed to\b|\bgo ahead\b/g) +
    countMatches(lower, /(?:^|[,.!?]\s*)don't\b/g); // clause-initial imperative "don't …", NOT hedging "I don't know"
  const uniq = new Set(words).size;
  const hasCode = /[`]|[a-zA-Z]:\\|https?:\/\/|\.(?:ts|md|json|mjs|js|ps1|sql)\b|\bCI-\d|^\s*\//m.test(text);
  const m = { wc, sc, filler, tagQ, hedge, selfcorr, directive, uniq, hasCode };
  m.mean_sentence_len = +(wc / sc).toFixed(2);
  m.filler_rate = +(wc ? (filler / wc) * 100 : 0).toFixed(2);
  m.hedge_rate = +(wc ? (hedge / wc) * 100 : 0).toFixed(2);
  m.ttr = +(wc ? uniq / wc : 0).toFixed(3);
  return m;
}
function voiceScore(m) {
  let s = 0;
  if (m.wc > 60) s++;
  if (m.filler_rate > 0) s++;
  if (m.tagQ > 0) s++;
  if (m.hedge >= 2) s++;
  if (m.hasCode) s--;
  if (m.wc < 12) s--;
  return s;
}

// ---------- time buckets ----------
function isoWeek(d) {
  const date = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  const dayNum = (date.getUTCDay() + 6) % 7;
  date.setUTCDate(date.getUTCDate() - dayNum + 3);
  const firstThursday = new Date(Date.UTC(date.getUTCFullYear(), 0, 4));
  const week = 1 + Math.round(((date - firstThursday) / 86400000 - 3 + ((firstThursday.getUTCDay() + 6) % 7)) / 7);
  return `${date.getUTCFullYear()}-W${String(week).padStart(2, '0')}`;
}

// ---------- main pass ----------
let totalLines = 0;
let userLines = 0;
const turns = [];
for (const file of sessionFiles) {
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  for (const line of lines) {
    if (!line.trim()) continue;
    totalLines++;
    let o;
    try { o = JSON.parse(line); } catch { continue; }
    if (o.type === 'user') userLines++;
    const t = extractTurn(o);
    if (!t) continue;
    if (since && t.ts && t.ts.slice(0, 10) < since) continue;
    t.m = metrics(t.text);
    t.score = voiceScore(t.m);
    t.voice = t.score >= 2;
    turns.push(t);
  }
}

// ---------- aggregate ----------
function newBucket() {
  return { turns: 0, voiceTurns: 0, wc: 0, filler: 0, hedge: 0, tagQ: 0, selfcorr: 0, directive: 0, slSum: 0, ttrSum: 0 };
}
function add(b, t) {
  b.turns++;
  if (t.voice) b.voiceTurns++;
  b.wc += t.m.wc;
  b.filler += t.m.filler;
  b.hedge += t.m.hedge;
  b.tagQ += t.m.tagQ;
  b.selfcorr += t.m.selfcorr;
  b.directive += t.m.directive;
  b.slSum += t.m.mean_sentence_len;
  b.ttrSum += t.m.ttr;
}
function finalize(b, bucket) {
  return {
    bucket,
    turns: b.turns,
    voice_share: +(b.turns ? b.voiceTurns / b.turns : 0).toFixed(3),
    filler_rate: +(b.wc ? (b.filler / b.wc) * 100 : 0).toFixed(2),
    hedge_rate: +(b.wc ? (b.hedge / b.wc) * 100 : 0).toFixed(2),
    tagQ_per_turn: +(b.turns ? b.tagQ / b.turns : 0).toFixed(2),
    selfcorr_per_turn: +(b.turns ? b.selfcorr / b.turns : 0).toFixed(2),
    directive_per_turn: +(b.turns ? b.directive / b.turns : 0).toFixed(2),
    mean_sentence_len: +(b.turns ? b.slSum / b.turns : 0).toFixed(2),
    mean_ttr: +(b.turns ? b.ttrSum / b.turns : 0).toFixed(3),
    avg_words: +(b.turns ? b.wc / b.turns : 0).toFixed(1),
  };
}

const overall = newBucket();
const byMonthRaw = {};
const byWeekRaw = {};
// Voice-only buckets: the un-diluted trend (typed commands/approvals drown the dictation signal
// in the all-turns buckets). Fed from the SAME loop, only when t.voice.
const overallVoice = newBucket();
const byMonthVoiceRaw = {};
const byWeekVoiceRaw = {};
for (const t of turns) {
  add(overall, t);
  if (t.voice) add(overallVoice, t);
  if (!t.ts) continue;
  const d = new Date(t.ts);
  if (Number.isNaN(+d)) continue;
  const mk = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
  const wk = isoWeek(d);
  (byMonthRaw[mk] ||= newBucket()) && add(byMonthRaw[mk], t);
  (byWeekRaw[wk] ||= newBucket()) && add(byWeekRaw[wk], t);
  if (t.voice) {
    (byMonthVoiceRaw[mk] ||= newBucket()) && add(byMonthVoiceRaw[mk], t);
    (byWeekVoiceRaw[wk] ||= newBucket()) && add(byWeekVoiceRaw[wk], t);
  }
}

const byMonth = Object.keys(byMonthRaw).sort().map((k) => finalize(byMonthRaw[k], k));
const byWeek = Object.keys(byWeekRaw).sort().map((k) => finalize(byWeekRaw[k], k));
const byMonthVoice = Object.keys(byMonthVoiceRaw).sort().map((k) => finalize(byMonthVoiceRaw[k], k));
const byWeekVoice = Object.keys(byWeekVoiceRaw).sort().map((k) => finalize(byWeekVoiceRaw[k], k));
// month-over-month deltas on the headline rates (same set applied to both all-turns and voice-only)
const deltaKeys = ['filler_rate', 'hedge_rate', 'tagQ_per_turn', 'voice_share', 'directive_per_turn'];
const applyDeltas = (buckets) => {
  for (let i = 1; i < buckets.length; i++) {
    buckets[i].deltas = {};
    for (const k of deltaKeys) buckets[i].deltas[k] = +(buckets[i][k] - buckets[i - 1][k]).toFixed(3);
  }
};
applyDeltas(byMonth);
applyDeltas(byMonthVoice);

// classifier confidence: share of turns NOT within ±1 of the decision boundary (score 2)
const near = turns.filter((t) => t.score === 1 || t.score === 2).length;
const splitConfidence = +(turns.length ? 1 - near / turns.length : 0).toFixed(3);
const voiceTurns = turns.filter((t) => t.voice);

const report = {
  generated: today,
  project: projectArg,
  corpus: { files: sessionFiles.length, totalLines, userLines, genuineTurns: turns.length, since: since || null },
  classifier: {
    voiceLikely: voiceTurns.length,
    voiceShare: +(turns.length ? voiceTurns.length / turns.length : 0).toFixed(3),
    nearThreshold: near,
    splitConfidence,
  },
  overall: finalize(overall, 'overall'),
  voiceOverall: finalize(overallVoice, 'voice-overall'),
  byMonth,
  byWeek,
  byMonthVoice,
  byWeekVoice,
};

// ---------- sanity guard: Pattern-37 backstop for injection leakage / implausible inflation ----------
// The marker-based exclusions in extractTurn are brittle; if a NEW injection type leaks into the voice
// set, catch it here instead of silently skewing the report.
const INJECTION_MARKERS = /^(?:base directory for this skill|this session is being continued|<task-notification|<ide_opened_file)/i;
const leaked = voiceTurns.filter((t) => INJECTION_MARKERS.test(t.text)).map((t) => t.text.slice(0, 60));
const warnings = [];
if (leaked.length) warnings.push(`possible injection leak in ${leaked.length} voice turn(s) — add an exclusion in extractTurn: ${JSON.stringify(leaked.slice(0, 3))}`);
if (report.voiceOverall.avg_words > 600) warnings.push(`voiceOverall.avg_words=${report.voiceOverall.avg_words} implausibly high — a new injection type or large paste may be leaking into the voice set; inspect the longest voice turns before trusting the report.`);
report.warnings = warnings;

// ---------- emit ----------
fs.mkdirSync(outDir, { recursive: true });
const metricsPath = path.join(outDir, `comms-coach-metrics-${today}.json`);
const samplePath = path.join(outDir, `comms-coach-sample-${today}.json`);
fs.writeFileSync(metricsPath, JSON.stringify(report, null, 2));

const sample = voiceTurns
  .filter((t) => t.ts)
  .sort((a, b) => (a.ts < b.ts ? 1 : -1))
  .slice(0, 25)
  .map((t) => ({
    ts: t.ts,
    sessionId: t.sessionId,
    score: t.score,
    wc: t.m.wc,
    filler_rate: t.m.filler_rate,
    hedge_rate: t.m.hedge_rate,
    tagQ: t.m.tagQ,
    text: t.text.length > 1400 ? t.text.slice(0, 1400) + ' …[truncated]' : t.text,
  }));
fs.writeFileSync(samplePath, JSON.stringify({ generated: today, count: sample.length, turns: sample }, null, 2));

const runLine = {
  date: today,
  corpus: 'project',
  files: sessionFiles.length,
  genuineTurns: turns.length,
  voiceLikely: voiceTurns.length,
  voiceShare: report.classifier.voiceShare,
  // delta source for the next run — VOICE-ONLY rates (the meaningful signal), not the diluted all-turns ones
  voice_filler_rate: report.voiceOverall.filler_rate,
  voice_hedge_rate: report.voiceOverall.hedge_rate,
  voice_tagQ_per_turn: report.voiceOverall.tagQ_per_turn,
  splitConfidence,
};
fs.appendFileSync(path.join(skillDir, 'runs.jsonl'), JSON.stringify(runLine) + '\n');

// ---------- stdout summary ----------
console.log('comms-coach Layer 1 —', today);
console.log(`  corpus: ${sessionFiles.length} session files, ${totalLines} lines, ${userLines} user-role lines`);
console.log(`  genuine human turns: ${turns.length} (${((turns.length / totalLines) * 100).toFixed(1)}% of lines)`);
console.log(`  voice-likely: ${voiceTurns.length} (${(report.classifier.voiceShare * 100).toFixed(0)}%), split confidence ${splitConfidence}`);
console.log(`  voice-only (the real signal): filler ${report.voiceOverall.filler_rate}/100w · hedge ${report.voiceOverall.hedge_rate}/100w · tagQ ${report.voiceOverall.tagQ_per_turn}/turn · directive ${report.voiceOverall.directive_per_turn}/turn`);
console.log(`  all-turns (diluted, for contrast): filler ${report.overall.filler_rate}/100w · hedge ${report.overall.hedge_rate}/100w · tagQ ${report.overall.tagQ_per_turn}/turn · meanTTR ${report.overall.mean_ttr}`);
console.log(`  months: ${byMonth.map((m) => m.bucket).join(', ')}`);
console.log(`  wrote: ${metricsPath}`);
console.log(`  wrote: ${samplePath}`);
console.log(`  appended: ${path.join(skillDir, 'runs.jsonl')}`);
if (warnings.length) { console.log('  ! warnings (Pattern-37 guard):'); for (const w of warnings) console.log(`    - ${w}`); }
