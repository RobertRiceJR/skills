/**
 * claude-cli-provider.cjs — promptfoo custom provider that grades through the Claude Code CLI.
 *
 * WHY THIS EXISTS: promptfoo's built-in Anthropic providers all require ANTHROPIC_API_KEY
 * (verified in promptfoo source — even anthropic:claude-agent-sdk throws without a key). There is
 * NO keyless path through them. This provider instead shells out to `claude -p`, which authenticates
 * with the logged-in Claude Code SUBSCRIPTION/OAuth session — no API key, billed against the plan.
 *   - Local runs: uses the existing interactive `claude` login.
 *   - Headless/CI: set CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`) so the CLI authenticates.
 * It is selected by lib.ts `graderProvider()` by default; set JUDGE_GRADER_MODE=api to use the
 * per-token first-party API path instead (requires ANTHROPIC_API_KEY).
 *
 * HOW: promptfoo's llm-rubric grader hands us the rendered rubric prompt (a JSON-stringified
 * [{role,content},...] chat array). We flatten it to one text prompt, pipe it to `claude -p` via
 * STDIN (no shell escaping of the quote/code-heavy artifact), and return the model's text — the
 * `{"reason","score","pass"}` object that llm-rubric then parses.
 *
 * LEAN FLAGS (keep per-call context small; the remainder caches across calls, 1h TTL):
 *   --allowed-tools ''                 → don't load tool definitions (~13K tokens)
 *   --strict-mcp-config --mcp-config   → empty MCP set, skip the project's 12 MCP servers
 *   cwd = os.tmpdir()                  → don't pick up the project CLAUDE.md
 *   --output-format json               → stable envelope; we read `.result`
 * We invoke the native `claude` binary directly (no shell — resolveClaudeBin() finds claude.exe on
 * Windows) and pass the whole prompt via stdin. A shell wrapper (claude.cmd/.ps1) silently dropped
 * stdin and hung every call; the native exe + piped stdin is reliable and needs no arg-escaping of
 * the code/quote-heavy artifact. The grader persona is the first chat message, flattened into stdin.
 */
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

// The CLI knows short aliases reliably; map the canonical ids the scripts use.
const MODEL_ALIASES = {
	'claude-haiku-4-5': 'haiku',
	'claude-haiku-4-5-20251001': 'haiku',
	'claude-sonnet-4-6': 'sonnet',
	'claude-opus-4-8': 'opus',
};

const EMPTY_MCP = path.join(__dirname, 'empty-mcp.json');

/** Find a directly-executable `claude` so we can run it WITHOUT a shell. A shell wrapper
 *  (claude.cmd/.ps1 on Windows) silently dropped piped stdin and hung every grade call. On Windows
 *  the native exe ships under the npm global tree; elsewhere `claude` on PATH is a real binary.
 *  Override with CLAUDE_BIN. Last resort: the shell shim (degraded — may hang). */
function resolveClaudeBin() {
	if (process.env.CLAUDE_BIN && fs.existsSync(process.env.CLAUDE_BIN)) return { bin: process.env.CLAUDE_BIN, shell: false };
	if (process.platform !== 'win32') return { bin: 'claude', shell: false };
	const candidates = [
		process.env.APPDATA && path.join(process.env.APPDATA, 'npm', 'node_modules', '@anthropic-ai', 'claude-code', 'bin', 'claude.exe'),
		process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'Programs', 'claude-code', 'claude.exe'),
	].filter(Boolean);
	for (const c of candidates) if (fs.existsSync(c)) return { bin: c, shell: false };
	return { bin: 'claude', shell: true };
}

const GRADE_TIMEOUT_MS = 180000; // kill a single grade after 3 min so one hang can't stall the whole run

/** Async spawn of one grade call — returns a Promise so promptfoo runs graders CONCURRENTLY.
 *  (The original spawnSync blocked Node's event loop, forcing every call to run serially despite
 *  promptfoo's concurrency setting.) Resolves { ok, stdout } or { ok:false, errorMsg }. */
function spawnClaude(bin, args, input, shell) {
	return new Promise((resolve) => {
		let child;
		try {
			child = spawn(bin, args, { cwd: os.tmpdir(), shell, windowsHide: true });
		} catch (e) {
			resolve({ ok: false, errorMsg: `claude CLI spawn failed: ${e && e.message ? e.message : String(e)}` });
			return;
		}
		const outChunks = [];
		const errChunks = [];
		let settled = false;
		const finish = (r) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			resolve(r);
		};
		const timer = setTimeout(() => {
			try {
				child.kill('SIGKILL');
			} catch {
				/* already gone */
			}
			finish({ ok: false, errorMsg: `claude CLI timed out after ${GRADE_TIMEOUT_MS}ms` });
		}, GRADE_TIMEOUT_MS);
		child.on('error', (e) => finish({ ok: false, errorMsg: `claude CLI error: ${e.message}` }));
		child.stdout.on('data', (d) => outChunks.push(d));
		child.stderr.on('data', (d) => errChunks.push(d));
		child.on('close', (code) => {
			const out = Buffer.concat(outChunks).toString('utf8');
			const err = Buffer.concat(errChunks).toString('utf8');
			if (code === 0) finish({ ok: true, stdout: out });
			else finish({ ok: false, errorMsg: `claude CLI exited ${code}: ${err.slice(0, 800)}` });
		});
		child.stdin.on('error', () => {
			/* swallow EPIPE if the child exits before we finish writing */
		});
		child.stdin.write(input);
		child.stdin.end();
	});
}

class ClaudeCliProvider {
	constructor(options = {}) {
		this.config = (options && options.config) || {};
		this.providerId = (options && options.id) || 'claude-cli';
	}

	id() {
		return this.providerId;
	}

	async callApi(prompt) {
		// Flatten the rubric prompt (JSON chat array, or a plain string) into one text prompt.
		let text = String(prompt);
		try {
			const parsed = JSON.parse(prompt);
			if (Array.isArray(parsed)) {
				const flat = parsed
					.map((m) => (typeof m === 'string' ? m : (m && m.content) || ''))
					.filter(Boolean)
					.join('\n\n');
				if (flat) text = flat;
			}
		} catch {
			/* not JSON — use the raw string */
		}

		const model = this.config.model || 'haiku';
		const cliModel = MODEL_ALIASES[model] || model;

		const args = [
			'-p',
			'--model',
			cliModel,
			'--output-format',
			'json',
			'--allowed-tools',
			'',
			'--strict-mcp-config',
			'--mcp-config',
			EMPTY_MCP,
		];

		const { bin, shell } = resolveClaudeBin();
		const r = await spawnClaude(bin, args, text, shell); // async → promptfoo grades concurrently
		if (!r.ok) return { error: r.errorMsg };

		// --output-format json → { type:'result', result:'<model text>', ... }. Fall back to raw stdout.
		let out = String(r.stdout || '');
		try {
			const env = JSON.parse(out);
			if (env && typeof env.result === 'string') out = env.result;
		} catch {
			/* not the envelope — use raw stdout */
		}

		// Strip a ```json … ``` fence if the model added one, so llm-rubric sees clean JSON.
		out = out
			.trim()
			.replace(/^```(?:json)?\s*/i, '')
			.replace(/\s*```$/i, '')
			.trim();

		return { output: out };
	}
}

module.exports = ClaudeCliProvider;
