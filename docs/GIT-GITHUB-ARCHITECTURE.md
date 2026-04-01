# Git & GitHub Architecture

Extracted from the Claude Code source code and findings. Every pattern includes exact file paths, line numbers, and step-by-step explanations.

---

## Table of Contents

1. [Git Operations Architecture](#git-operations-architecture)
2. [GitHub Integration Architecture](#github-integration-architecture)
3. [Version Control Patterns](#version-control-patterns)
4. [Undercover Mode for Git](#undercover-mode-for-git)
5. [Edge Cases Handled](#edge-cases-handled)

---

## Git Operations Architecture

### How Git Commands Are Executed

**Pattern: `execFileNoThrow` wrapper with memoized binary resolution**

- **File**: `src/src/utils/git.ts:212-216`
- **Code**:
  ```ts
  export const gitExe = memoize((): string => {
    return whichSync('git') || 'git'
  })
  ```
- **How it works**:
  1. `whichSync('git')` resolves the full path to the git binary once
  2. Result is memoized so subsequent calls skip the PATH lookup
  3. Falls back to bare `'git'` string if not found (relies on PATH)
- **Why**: Every subprocess spawn requires a binary path lookup. Memoizing avoids repeated PATH scans across hundreds of git invocations per session.
- **AgentOS adaptation**: Use a similar memoized binary resolver for any CLI tool you invoke frequently.

**Pattern: All git commands use `execFileNoThrow` (not BashTool)**

- **Files**: `src/src/utils/git.ts` (throughout), `src/src/utils/gitDiff.ts` (throughout), `src/src/utils/worktree.ts` (throughout)
- **How it works**:
  1. Commands are built as argument arrays: `['--no-optional-locks', 'status', '--porcelain']`
  2. `execFileNoThrow(gitExe(), args, options)` spawns the process directly
  3. Returns `{ stdout, stderr, code }` — never throws on non-zero exit
  4. `preserveOutputOnError: false` prevents leaking sensitive output on failure
- **Why**: Direct subprocess invocation is faster than going through a shell. Argument arrays prevent shell injection. `execFileNoThrow` ensures graceful degradation.
- **AgentOS adaptation**: Never shell-construct git commands. Always use argument arrays with a no-throw wrapper.

**Pattern: `--no-optional-locks` flag on all status/diff commands**

- **File**: `src/src/utils/git.ts:359`, `src/src/utils/git.ts:372`, `src/src/utils/gitDiff.ts:64`
- **Code**: `['--no-optional-locks', 'status', '--porcelain']`
- **How it works**: Prevents git from acquiring optional locks that could conflict with concurrent git operations (e.g., the user running git in another terminal)
- **Why**: Claude Code may be reading git state while the user is simultaneously committing/pushing. Optional locks would cause spurious failures.
- **AgentOS adaptation**: Always use `--no-optional-locks` for read-only git operations.

### How Git State Is Tracked and Managed

**Pattern: `GitRepoState` aggregate type**

- **File**: `src/src/utils/git.ts:463-470`
- **Code**:
  ```ts
  export type GitRepoState = {
    commitHash: string
    branchName: string
    remoteUrl: string | null
    isHeadOnRemote: boolean
    isClean: boolean
    worktreeCount: number
  }
  ```
- **How it works**:
  1. `getGitState()` (line 472-502) runs 6 git commands in parallel via `Promise.all`
  2. Returns `null` on any failure (best-effort)
  3. Used for analytics, session persistence, and UI state
- **Why**: Single parallel call instead of 6 serial calls. Null-on-failure prevents cascading errors.
- **AgentOS adaptation**: Aggregate related state queries into a single parallel call.

**Pattern: Cached filesystem-based git operations**

- **File**: `src/src/utils/git.ts:13-20`
- **Imports**: `getCachedBranch`, `getCachedHead`, `getCachedDefaultBranch`, `getCachedRemoteUrl`, `resolveGitDir` from `./git/gitFilesystem.js`
- **How it works**: Instead of spawning `git branch --show-current`, the code reads `.git/HEAD` and `.git/refs/` directly from the filesystem
- **Why**: Subprocess spawn costs ~15ms. File reads are <1ms. For polling scenarios (status bar, diff display), this is critical.
- **AgentOS adaptation**: Read git internals directly for hot-path operations; use subprocess only for mutations.

**Pattern: LRU-memoized `findGitRoot`**

- **File**: `src/src/utils/git.ts:27-86`
- **How it works**:
  1. Walks up the directory tree from `startPath`, checking for `.git` at each level
  2. Accepts both `.git` directories (regular repos) and `.git` files (worktrees/submodules)
  3. Results cached with LRU (max 50 entries) via `memoizeWithLRU`
  4. Returns `GIT_ROOT_NOT_FOUND` symbol (not null) internally to distinguish "not found" from "found null"
  5. Normalizes paths to NFC form for macOS compatibility
- **Why**: Called on every file edit, permission check, and prompt build. LRU prevents unbounded growth when editing files across many directories.
- **AgentOS adaptation**: Use LRU caching for directory-walk operations. Normalize paths to NFC on macOS.

### How Git Errors Are Handled

**Pattern: `execFileNoThrow` with `preserveOutputOnError: false`**

- **File**: `src/src/utils/execFileNoThrow.js` (referenced throughout)
- **How it works**:
  1. Never throws on non-zero exit codes
  2. Returns `{ stdout, stderr, code }` tuple
  3. `preserveOutputOnError: false` prevents leaking sensitive data (tokens, paths) in error output
  4. Callers check `code === 0` to determine success
- **Why**: Git operations are best-effort in a coding assistant context. A failed `git status` shouldn't crash the session.
- **AgentOS adaptation**: Wrap all external tool calls in no-throw wrappers. Never expose stderr to users.

**Pattern: Graceful degradation chains**

- **File**: `src/src/utils/git.ts:562-603` (`findRemoteBase`)
- **How it works**:
  1. First try: `git rev-parse --abbrev-ref --symbolic-full-name @{u}` (tracking branch)
  2. Second try: `git remote show origin -- HEAD` (parse default branch)
  3. Third try: Check `origin/main`, `origin/staging`, `origin/master` existence
  4. Returns `null` if all fail
- **Why**: Different repo configurations support different discovery methods. Cascading fallbacks maximize compatibility.
- **AgentOS adaptation**: Build fallback chains for all external service queries.

### How Git Hooks Are Managed

**Pattern: Worktree hook path propagation**

- **File**: `src/src/utils/worktree.ts:536-578`
- **How it works**:
  1. After creating a worktree, searches for `.husky/` or `.git/hooks/` in the main repo
  2. Sets `core.hooksPath` to the absolute path of the hooks directory
  3. Skips the `git config` subprocess if the value already matches (idempotent, saves ~14ms)
  4. Writes to the shared `.git/config` (not worktree-local), so all worktrees inherit it
- **Why**: Husky and other hook frameworks use relative paths. In a worktree, relative paths resolve to the worktree directory, not the main repo, causing hooks to fail.
- **AgentOS adaptation**: Always use absolute paths for hook configurations in multi-root setups.

**Pattern: Attribution hook installation in worktrees**

- **File**: `src/src/utils/worktree.ts:598-623`
- **How it works**:
  1. Installs `prepare-commit-msg` hook directly into the worktree's `.husky/` directory
  2. Passes worktree-local `.husky` path explicitly (not the shared config value)
  3. Uses dynamic `import()` behind `feature('COMMIT_ATTRIBUTION')` gate
  4. Double error handling: inner `.catch` for hook install failure, outer `.catch` for module load failure
- **Why**: Husky's `prepare` script resets `core.hooksPath` on every `bun install`. Direct installation is resilient to this.
- **AgentOS adaptation**: Install hooks directly into target directories, not via config references that can be overwritten.

**Pattern: Git safety protocol in prompts**

- **File**: `src/src/commands/commit.ts:27-35`, `src/src/commands/commit-push-pr.ts:67-74`
- **Rules enforced via prompt instructions**:
  - NEVER update git config
  - NEVER skip hooks (`--no-verify`, `--no-gpg-sign`) unless user explicitly requests
  - ALWAYS create NEW commits, NEVER `--amend` unless user explicitly requests
  - Do not commit files likely containing secrets (.env, credentials.json)
  - Never use `-i` flags (interactive mode not supported)
  - NEVER force push to main/master
- **Why**: The model generates git commands via prompts, not hardcoded logic. Safety rules must be in the prompt to prevent destructive operations.
- **AgentOS adaptation**: Embed safety constraints directly in AI prompts that generate shell commands.

### How Git Configuration Is Loaded

**Pattern: Settings-driven git behavior**

- **File**: `src/src/utils/gitSettings.ts:1-18`
- **How it works**:
  1. `shouldIncludeGitInstructions()` checks `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS` env var
  2. Falls back to `settings.includeGitInstructions` config
  3. Lives in a separate file to avoid import cycles (git.ts → settings.ts → git/gitignore.ts → git.ts)
  4. Also avoids pulling `@opentelemetry/api` + `undici` into the VS Code extension (forbidden deps)
- **Why**: Import cycle prevention and VS Code extension dependency constraints dictate file placement.
- **AgentOS adaptation**: Isolate settings-dependent utilities to avoid import cycles.

**Pattern: Git config parsing from filesystem**

- **File**: `src/src/utils/worktree.ts:556-560`
- **How it works**:
  1. `resolveGitDir(repoRoot)` gets the git directory path
  2. `getCommonDir(gitDir)` resolves the shared config directory for worktrees
  3. `parseGitConfigValue(configDir, 'core', null, 'hooksPath')` reads the config file directly
  4. Compares existing value before writing (idempotent optimization)
- **Why**: Reading config from files is faster than spawning `git config --get`. Idempotent checks save subprocess overhead.
- **AgentOS adaptation**: Read config files directly when possible; compare before writing.

### How Git Authentication Works

**Pattern: Non-interactive git environment**

- **File**: `src/src/utils/worktree.ts:195-202`
- **Code**:
  ```ts
  const GIT_NO_PROMPT_ENV = {
    GIT_TERMINAL_PROMPT: '0',
    GIT_ASKPASS: '',
  }
  ```
- **How it works**:
  1. `GIT_TERMINAL_PROMPT=0` prevents git from opening `/dev/tty` for credential prompts
  2. `GIT_ASKPASS=''` disables askpass GUI programs
  3. `stdin: 'ignore'` closes stdin so interactive prompts can't block
  4. Applied to all `git fetch` operations during worktree creation
- **Why**: A hanging credential prompt would freeze the entire CLI session. These env vars ensure git fails fast instead of waiting for input.
- **AgentOS adaptation**: Always set non-interaction env vars when spawning git in automated contexts.

**Pattern: `gh` auth status detection**

- **File**: `src/src/utils/github/ghAuthStatus.ts:1-29`
- **How it works**:
  1. Uses `which('gh')` (no subprocess) to detect if `gh` CLI is installed
  2. Runs `gh auth token` (not `gh auth status`) to check authentication
  3. `stdout: 'ignore'` ensures the token never enters the process memory
  4. Exit code 0 = authenticated, non-zero = not authenticated
- **Why**: `gh auth status` makes a network request to GitHub's API. `gh auth token` only reads local config/keyring — faster and more reliable offline.
- **AgentOS adaptation**: Use local-only auth checks when possible. Never load tokens into process memory.

---

## GitHub Integration Architecture

### How GitHub API Calls Are Made

**Pattern: `gh` CLI as the GitHub API client**

- **File**: `src/src/utils/ghPrStatus.ts:58-69`
- **How it works**:
  1. All GitHub API calls go through the `gh` CLI, not direct HTTP requests
  2. `gh pr view --json number,url,reviewDecision,isDraft,headRefName,state`
  3. JSON output is parsed with `jsonParse(stdout)`
  4. 5-second timeout prevents hanging on network issues
- **Why**: `gh` handles authentication, rate limiting, and API versioning automatically. No need to manage tokens or API versions.
- **AgentOS adaptation**: Prefer `gh` CLI over direct API calls for GitHub operations.

**Pattern: PR reference parsing**

- **File**: `src/src/utils/worktree.ts:633-651`
- **How it works**:
  1. Accepts GitHub-style URLs: `https://github.com/owner/repo/pull/123`
  2. Accepts `#N` format: `#123`
  3. Regex extracts the PR number from either format
  4. Returns `null` for unrecognized formats
- **Why**: Users reference PRs in multiple ways. Unified parsing enables worktree creation from any PR reference.
- **AgentOS adaptation**: Support multiple input formats for user-facing references.

### How PRs Are Created and Managed

**Pattern: Prompt-driven PR creation**

- **File**: `src/src/commands/commit-push-pr.ts:26-106`
- **How it works**:
  1. The command builds a prompt with git context (status, diff, branch, recent commits)
  2. The model generates `gh pr create` or `gh pr edit` commands
  3. HEREDOC syntax used for PR body to handle multiline content safely
  4. PR template includes: Summary, Test plan, Changelog sections
  5. If PR already exists, uses `gh pr edit` to update title/body
  6. Adds `--reviewer anthropics/claude-code` for internal repos
- **Why**: Prompt-driven approach lets the model adapt PR descriptions to the actual changes. HEREDOC prevents shell escaping issues with multiline content.
- **AgentOS adaptation**: Use HEREDOC syntax for multiline shell arguments. Let AI generate PR content based on actual diffs.

**Pattern: PR status fetching with smart filtering**

- **File**: `src/src/utils/ghPrStatus.ts:46-106`
- **How it works**:
  1. Skips if not in a git repo
  2. Skips if on the default branch (would show the most recently merged PR, which is misleading)
  3. Skips if PR's head branch is `main`/`master`
  4. Skips if PR state is `MERGED` or `CLOSED`
  5. Derives review state: draft → `draft`, APPROVED → `approved`, CHANGES_REQUESTED → `changes_requested`, else → `pending`
- **Why**: Many edge cases produce misleading PR status. Filtering ensures only relevant, open PRs are displayed.
- **AgentOS adaptation**: Filter PR status aggressively to avoid showing stale or irrelevant information.

### How Commits Are Attributed

**Pattern: Character-level contribution tracking**

- **File**: `src/src/utils/commitAttribution.ts:324-380`
- **How it works**:
  1. On every file edit, computes Claude's character contribution using common prefix/suffix matching
  2. Finds the changed region by comparing old and new content
  3. Handles same-length replacements (e.g., "Esc" → "esc") where length diff would be 0
  4. Accumulates contributions per file in a `Map<string, FileAttributionState>`
  5. On commit, calculates `claudePercent = claudeChars / (claudeChars + humanChars) * 100`
- **Why**: Character-level tracking is more accurate than line-level or file-level. Prefix/suffix matching correctly identifies the actual changed region.
- **AgentOS adaptation**: Track contributions at the character level using diff algorithms for accurate attribution.

**Pattern: Attribution text generation**

- **File**: `src/src/utils/attribution.ts:52-98`
- **How it works**:
  1. `getAttributionTexts()` returns `{ commit, pr }` strings
  2. Commit attribution: `Co-Authored-By: <model> <noreply@anthropic.com>`
  3. PR attribution: `🤖 Generated with [Claude Code](https://claude.ai/claude-code)`
  4. Custom attribution via `settings.attribution.commit/pr`
  5. Backward compatibility with deprecated `includeCoAuthoredBy` setting
  6. Undercover mode returns empty strings
- **Why**: Git trailers (`Co-Authored-By:`) are standard for co-authorship. PR attribution uses markdown links for clickability.
- **AgentOS adaptation**: Use standard git trailer format for commit attribution.

**Pattern: Enhanced PR attribution with stats**

- **File**: `src/src/utils/attribution.ts:297-393`
- **How it works**:
  1. Reads session transcript to count user prompts (N-shot count)
  2. Counts memory file accesses
  3. Computes Claude contribution percentage
  4. Format: `🤖 Generated with [Claude Code](...) (93% 3-shotted by claude-opus-4-5, 2 memories recalled)`
  5. For internal repos, appends git trailers via `buildPRTrailers()`
- **Why**: Users want to know how much Claude contributed. N-shot count and percentage provide concrete metrics.
- **AgentOS adaptation**: Compute and display contribution metrics for AI-assisted work.

**Pattern: Model name sanitization**

- **File**: `src/src/utils/commitAttribution.ts:154-168`
- **How it works**:
  1. Maps internal model codenames to public names
  2. `opus-4-6` → `claude-opus-4-6`, `sonnet-4-5` → `claude-sonnet-4-5`, etc.
  3. Unknown models get generic `claude` name
  4. Only internal repos (allowlisted) get real model names
- **Why**: Internal codenames are confidential. Public repos must never see them.
- **AgentOS adaptation**: Sanitize internal identifiers before exposing them in public outputs.

### How GitHub Authentication Works

**Pattern: `gh` CLI authentication**

- **File**: `src/src/utils/github/ghAuthStatus.ts:17-28`
- **How it works**:
  1. Checks if `gh` is installed via `which()`
  2. Runs `gh auth token` to verify authentication
  3. `stdout: 'ignore'` prevents token from entering process memory
  4. Returns `'authenticated' | 'not_authenticated' | 'not_installed'`
- **Why**: `gh` manages its own auth (OAuth tokens, keyring integration). No need to handle token storage or rotation.
- **AgentOS adaptation**: Delegate authentication to existing CLI tools rather than managing tokens directly.

### How GitHub Webhooks Are Handled

**Pattern: Remote review via webhook-triggered sessions**

- **File**: `src/src/commands/review/reviewRemote.ts:128-316`
- **How it works**:
  1. `/ultrareview` command can launch a remote review session
  2. PR mode: uses `refs/pull/N/head` to checkout the PR branch
  3. Branch mode: bundles the working tree and sends merge-base SHA
  4. Remote session runs in a cloud container with bughunter configuration
  5. Results arrive via `task-notification` back to the local session
- **Why**: Heavy review tasks (multiple agents, verification loops) require cloud resources. Local session stays responsive.
- **AgentOS adaptation**: Offload heavy analysis tasks to remote sessions with result callbacks.

### How GitHub Actions Integration Works

**Pattern: No direct GitHub Actions integration found**

The codebase does not contain direct GitHub Actions integration. The `gh` CLI is used for PR/issue operations, but Actions workflows are not managed programmatically.

---

## Version Control Patterns

### Branch Management

**Pattern: Default branch detection with cascading fallbacks**

- **File**: `src/src/utils/git.ts:562-603`
- **How it works**:
  1. First: tracking branch (`@{u}`)
  2. Second: `git remote show origin -- HEAD` (parse "HEAD branch: ...")
  3. Third: Check `origin/main`, `origin/staging`, `origin/master` existence
- **Why**: Different repos have different default branch names and tracking configurations.
- **AgentOS adaptation**: Use cascading detection for branch names.

**Pattern: Branch naming for worktrees**

- **File**: `src/src/utils/worktree.ts:217-227`
- **How it works**:
  1. Slug is flattened: `user/feature` → `user+feature` (`+` is valid in git branch names but not in slug segments)
  2. Branch name: `worktree-<flattened-slug>` (e.g., `worktree-user+feature`)
  3. Path: `.claude/worktrees/<flattened-slug>`
  4. Prevents D/F conflicts (file vs directory in git refs)
- **Why**: Nested slugs cause git ref conflicts and filesystem nesting issues. Flattening with `+` is injective and safe.
- **AgentOS adaptation**: Flatten hierarchical names into flat identifiers using safe separator characters.

**Pattern: Branch command (conversation forking)**

- **File**: `src/src/commands/branch/branch.ts:61-173`
- **How it works**:
  1. Reads current transcript JSONL
  2. Filters to main conversation messages (excludes sidechains)
  3. Creates new session with new UUID, preserving all metadata
  4. Adds `forkedFrom` traceability (original sessionId + messageUuid)
  5. Preserves content-replacement records to avoid prompt cache misses
  6. Handles title collisions with numbered suffixes
- **Why**: Conversation forking requires exact state preservation. Content-replacement records are critical for cache efficiency.
- **AgentOS adaptation**: Preserve all metadata when forking/cloning state. Track parent-child relationships.

### Worktree Isolation

**Pattern: Worktree creation with post-setup**

- **File**: `src/src/utils/worktree.ts:235-375`
- **How it works**:
  1. Validates slug against path traversal (allowlist: `[a-zA-Z0-9._-]`)
  2. Fast resume: reads `.git` pointer file directly (no subprocess)
  3. New worktree: `git worktree add -B <branch> <path> <baseBranch>`
  4. `-B` (not `-b`): resets orphan branches left by removed worktrees
  5. Post-setup: copies `settings.local.json`, configures hooks, symlinks directories, copies `.worktreeinclude` files
  6. Sparse checkout support via `settings.worktree.sparsePaths`
- **Why**: Worktrees provide isolated working directories sharing the same git object store. Post-setup ensures consistent environment.
- **AgentOS adaptation**: Use worktrees for isolated development environments with shared state.

**Pattern: Worktree session tracking**

- **File**: `src/src/utils/worktree.ts:140-169`
- **How it works**:
  1. `currentWorktreeSession` global tracks active session
  2. Includes: original cwd, worktree path, branch, head commit, session ID, tmux session
  3. Persisted to project config for resume
  4. `restoreWorktreeSession()` re-establishes session on `--resume`
- **Why**: Session persistence across restarts requires tracking the worktree context.
- **AgentOS adaptation**: Track isolation context for session persistence.

**Pattern: Agent worktree creation (lightweight)**

- **File**: `src/src/utils/worktree.ts:902-952`
- **How it works**:
  1. `createAgentWorktree()` creates worktrees without touching global session state
  2. Uses `findCanonicalGitRoot` (not `findGitRoot`) so agent worktrees always land in the main repo's `.claude/worktrees/`
  3. Bumps mtime on resume to prevent stale cleanup
  4. Does NOT `process.chdir` or update project config
- **Why**: Subagents need isolated worktrees but shouldn't affect the parent session's context.
- **AgentOS adaptation**: Create lightweight isolation contexts for sub-tasks that don't affect parent state.

**Pattern: Stale agent worktree cleanup**

- **File**: `src/src/utils/worktree.ts:1030-1136`
- **How it works**:
  1. Scans `.claude/worktrees/` for ephemeral slugs matching patterns: `agent-a[7hex]`, `wf_<uuid>-<idx>`, `bridge-<id>`, `job-<name>-<8hex>`
  2. Skips current session's worktree
  3. Checks mtime against cutoff date
  4. Fail-closed: skips if git status fails or shows tracked changes
  5. Fail-closed: skips if commits aren't reachable from a remote
  6. Uses `git worktree remove --force` + `git worktree prune`
- **Why**: Crashed processes leave orphaned worktrees. Pattern-based cleanup avoids deleting user-named worktrees.
- **AgentOS adaptation**: Use pattern matching to identify and clean up orphaned resources.

### Cross-Project Resume

**Pattern: Cross-project resume detection**

- **File**: `src/src/utils/crossProjectResume.ts:30-75`
- **How it works**:
  1. Compares `log.projectPath` with `currentCwd`
  2. Checks if `log.projectPath` is under a worktree of the same repo
  3. If same repo worktree: resume directly (no `cd` needed)
  4. If different repo: generates `cd <path> && claude --resume <sessionId>` command
  5. Worktree detection gated to `USER_TYPE === 'ant'` for staged rollout
- **Why**: Resuming a session from a different directory requires context about whether it's the same repo (worktree) or different project.
- **AgentOS adaptation**: Detect isolation boundaries when resuming cross-context sessions.

### Commit Message Generation

**Pattern: Prompt-driven commit message generation**

- **File**: `src/src/commands/commit.ts:12-54`
- **How it works**:
  1. Prompt includes: `git status`, `git diff HEAD`, current branch, recent commits
  2. Model analyzes changes and drafts commit message
  3. Looks at recent commits to match repository's commit message style
  4. Summarizes nature of changes (feature, enhancement, bug fix, etc.)
  5. Focuses on "why" rather than "what"
  6. Uses HEREDOC syntax for multiline commit messages
  7. Appends attribution text (`Co-Authored-By:`) if configured
- **Why**: Model-generated commit messages are context-aware and match project conventions.
- **AgentOS adaptation**: Use AI to generate commit messages based on actual diffs and project history.

### PR Description Generation

**Pattern: Prompt-driven PR description generation**

- **File**: `src/src/commands/commit-push-pr.ts:26-106`
- **How it works**:
  1. Prompt includes: `git diff <defaultBranch>...HEAD` (all commits in PR)
  2. Model generates PR title (short, under 70 chars) and body
  3. Body template: Summary (1-3 bullets), Test plan (checklist), Changelog (conditional)
  4. HEREDOC syntax for safe multiline body
  5. Adds attribution and reviewer for internal repos
  6. Slack integration: checks CLAUDE.md for Slack posting instructions
- **Why**: PR descriptions should summarize the entire diff, not just the latest commit. Template ensures consistency.
- **AgentOS adaptation**: Generate PR descriptions from branch diffs, not single commits.

---

## Undercover Mode for Git

### How Undercover Mode Strips Attribution

**Pattern: Activation logic**

- **File**: `src/src/utils/undercover.ts:28-37`
- **How it works**:
  1. `isUndercover()` returns `true` if:
     - `CLAUDE_CODE_UNDERCOVER=1` env var is set (force ON)
     - OR repo class is not `'internal'` (auto-detection)
  2. Auto-detection: active UNLESS repo remote matches `INTERNAL_MODEL_REPOS` allowlist
  3. Safe default is ON — if not confident we're in an internal repo, stay undercover
  4. All code paths gated on `USER_TYPE === 'ant'` (build-time constant-folded)
- **Why**: Safe default prevents accidental leaks. Build-time gating removes all undercover code from external builds.
- **AgentOS adaptation**: Use safe-default activation for security-sensitive modes.

**Pattern: Attribution stripping in commit/PR prompts**

- **File**: `src/src/commands/commit.ts:16-18`, `src/src/commands/commit-push-pr.ts:49-55`
- **How it works**:
  1. When undercover, `getUndercoverInstructions()` is prepended to the prompt
  2. `getAttributionTexts()` returns empty strings for commit and PR
  3. `getEnhancedPRAttribution()` returns empty string
  4. Reviewer argument (`--reviewer anthropics/claude-code`) is removed
  5. Changelog section is removed
  6. Slack integration step is removed
- **Why**: All attribution, reviewer, and integration features are stripped to prevent any internal information from appearing in public repos.
- **AgentOS adaptation**: Strip all identifying information when operating in untrusted contexts.

### How It Prevents Internal Info Leaks

**Pattern: Undercover instructions**

- **File**: `src/src/utils/undercover.ts:39-72`
- **What's forbidden in commit messages and PR descriptions**:
  - Internal model codenames (animal names like Capybara, Tengu)
  - Unreleased model version numbers (opus-4-7, sonnet-4-8)
  - Internal repo or project names (claude-cli-internal, anthropics/...)
  - Internal tooling, Slack channels, short links (go/cc, #claude-code-...)
  - The phrase "Claude Code" or any AI mention
  - Model version hints
  - Co-Authored-By lines or any attribution
- **Why**: Comprehensive list prevents the model from accidentally leaking any internal information.
- **AgentOS adaptation**: Provide explicit negative examples of what NOT to include.

**Pattern: Model name sanitization**

- **File**: `src/src/utils/commitAttribution.ts:154-168`
- **How it works**:
  1. `sanitizeModelName()` maps internal variants to public names
  2. Unknown models get generic `claude` name
  3. Only internal repos (allowlisted in `INTERNAL_MODEL_REPOS`) get real model names
- **Why**: Double protection: undercover mode strips attribution entirely, and sanitization provides a fallback for edge cases.
- **AgentOS adaptation**: Sanitize identifiers at multiple layers for defense in depth.

### How It Handles Commit Messages

**Pattern: No attribution appended**

- **File**: `src/src/commands/commit.ts:49`
- **How it works**:
  1. When undercover, `commitAttribution` is empty string
  2. HEREDOC template: `git commit -m "$(cat <<'EOF'\nCommit message here.\nEOF\n)"`
  3. No `Co-Authored-By:` line is appended
- **Why**: Clean commit messages with no AI attribution in public repos.
- **AgentOS adaptation**: Conditionally append metadata based on trust context.

### How It Handles PR Descriptions

**Pattern: No attribution, no reviewer, no changelog**

- **File**: `src/src/commands/commit-push-pr.ts:49-55`
- **How it works**:
  1. `reviewerArg` set to empty (no `--reviewer anthropics/claude-code`)
  2. `addReviewerArg` set to empty (no `--add-reviewer`)
  3. `changelogSection` set to empty
  4. `slackStep` set to empty
  5. PR body template: just Summary and Test plan
- **Why**: All internal-specific features are removed from PR creation in public repos.
- **AgentOS adaptation**: Conditionally include/exclude PR features based on repo trust level.

---

## Edge Cases Handled

### Detached HEAD State

**Pattern: `preserveGitStateForIssue` fallback**

- **File**: `src/src/utils/git.ts:724-845`
- **How it works**:
  1. `findRemoteBase()` tries tracking branch first, which may not exist in detached HEAD
  2. Falls back to `git remote show origin -- HEAD`
  3. Falls back to checking common branch names
  4. If `merge-base` fails, uses HEAD-only mode (patch from HEAD, no remote base)
  5. Branch name is set to `null` if it equals `'HEAD'`
- **Why**: Detached HEAD state is common for CI, crash repros, and bisect operations. HEAD-only mode preserves what's possible.
- **AgentOS adaptation**: Provide graceful degradation for detached HEAD operations.

### Bare Repositories

**Pattern: Bare repo detection for security**

- **File**: `src/src/utils/git.ts:876-925`
- **How it works**:
  1. Checks if `.git/HEAD` is a valid file (not directory)
  2. If `.git/HEAD` is invalid, checks if cwd has bare git indicators: `HEAD` file, `objects/` dir, `refs/` dir
  3. Returns `true` if cwd looks like a bare/exploited git directory
  4. Worktrees (`.git` is a file) are correctly excluded
- **Why**: Security: an attacker can create bare git indicators in cwd to trick git into executing hooks from the current directory (sandbox escape).
- **AgentOS adaptation**: Detect and reject manipulated repository structures.

**Pattern: Bare repo worktree resolution**

- **File**: `src/src/utils/git.ts:171-176`
- **How it works**:
  1. In `resolveCanonicalRoot`, if `basename(commonDir) !== '.git'`, the common dir itself is returned
  2. This handles bare-repo worktrees where the common dir isn't inside a working directory
- **Why**: Bare repos don't have a working directory, so the common dir IS the repo identity.
- **AgentOS adaptation**: Handle bare repo worktrees as a special case in path resolution.

### Shallow Clones

**Pattern: Shallow clone detection and fallback**

- **File**: `src/src/utils/git.ts:608-610`, `src/src/utils/git.ts:731-747`
- **How it works**:
  1. `isShallowClone()` checks for `<gitDir>/shallow` file existence
  2. In `preserveGitStateForIssue()`, shallow clones fall back to HEAD-only mode
  3. Returns `remote_base_sha: null`, `remote_base: null`, `format_patch: null`
  4. Still captures `patch` (diff from HEAD) and `untracked_files`
- **Why**: Shallow clones don't have full history, so merge-base and format-patch operations fail. HEAD-only mode preserves what's possible.
- **AgentOS adaptation**: Detect shallow clones and adjust operations accordingly.

### Submodules

**Pattern: Submodule detection in canonical root resolution**

- **File**: `src/src/utils/git.ts:117-119`, `src/src/utils/git.ts:137-138`
- **How it works**:
  1. Submodules have `.git` as a file (like worktrees) but no `commondir` file
  2. `readFileSync(join(worktreeGitDir, 'commondir'))` throws ENOENT for submodules
  3. Falls through to returning the input root (submodules are separate repos)
- **Why**: Submodules are independent git repositories. They should not be resolved to the parent repo's working directory.
- **AgentOS adaptation**: Distinguish submodules from worktrees by checking for `commondir` file.

### Large Repos

**Pattern: Diff size limits**

- **File**: `src/src/utils/gitDiff.ts:35-40`
- **Constants**:
  - `GIT_TIMEOUT_MS = 5000`
  - `MAX_FILES = 50`
  - `MAX_DIFF_SIZE_BYTES = 1_000_000` (1 MB)
  - `MAX_LINES_PER_FILE = 400`
  - `MAX_FILES_FOR_DETAILS = 500`
- **How it works**:
  1. Quick probe with `--shortstat` to detect massive diffs
  2. If > 500 files, returns totals only (no per-file details)
  3. If > 50 files, limits per-file stats
  4. Files > 1MB are skipped entirely
  5. Files ≤ 1MB are limited to 400 lines of hunk content
- **Why**: Large repos (jj workspaces, monorepos) can produce diffs with hundreds of thousands of files. Limits prevent memory exhaustion.
- **AgentOS adaptation**: Implement progressive limits: quick probe → totals → per-file → detailed.

**Pattern: Untracked file capture limits**

- **File**: `src/src/utils/git.ts:548-556`
- **Constants**:
  - `MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024` (500MB per file)
  - `MAX_TOTAL_SIZE_BYTES = 5 * 1024 * 1024 * 1024` (5GB total)
  - `MAX_FILE_COUNT = 20000`
  - `SNIFF_BUFFER_SIZE = 64 * 1024` (64KB)
- **How it works**:
  1. Binary detection via extension check (zero I/O)
  2. Binary sniff on first 64KB of content
  3. Per-file and total size limits enforced
  4. File count limit prevents processing thousands of files
  5. If file fits in sniff buffer, reuses it; otherwise reads with encoding (avoids full Buffer allocation)
- **Why**: Prevents memory exhaustion from large untracked files while preserving content capture for reasonable files.
- **AgentOS adaptation**: Use sniff buffers for binary detection. Reuse buffers when possible.

### Permission Issues

**Pattern: Fail-closed worktree cleanup**

- **File**: `src/src/utils/worktree.ts:1098-1118`
- **How it works**:
  1. Stale worktree cleanup checks `git status --porcelain -uno` and `git rev-list --max-count=1 HEAD --not --remotes`
  2. Both must succeed with empty output
  3. Non-zero exit (corrupted worktree, permission denied) means skip
  4. Fail-closed: if unsure what's in there, don't delete it
- **Why**: Deleting a worktree with uncommitted work would be destructive. Permission errors indicate something is wrong.
- **AgentOS adaptation**: Fail-closed for destructive operations. When in doubt, don't delete.

**Pattern: Symlink directory error handling**

- **File**: `src/src/utils/worktree.ts:107-138`
- **How it works**:
  1. Validates directory doesn't escape repository boundaries (`containsPathTraversal`)
  2. Silently skips if source doesn't exist (ENOENT) or destination already exists (EEXIST)
  3. Logs warnings for unexpected errors (permission denied, unsupported platform)
- **Why**: Symlinking is best-effort. Missing source directories are expected; permission errors should be logged but not fatal.
- **AgentOS adaptation**: Validate paths for traversal before creating symlinks.

### Network Issues

**Pattern: Fetch with no-prompt environment**

- **File**: `src/src/utils/worktree.ts:260-301`
- **How it works**:
  1. `GIT_TERMINAL_PROMPT=0` and `GIT_ASKPASS=''` prevent interactive prompts
  2. `stdin: 'ignore'` closes stdin
  3. If fetch fails, falls back to `HEAD` as base branch
  4. If `origin/<branch>` already exists locally, skips fetch entirely (saves ~6-8s in large repos)
- **Why**: Network operations can hang waiting for credentials. Non-interaction env vars ensure fast failure.
- **AgentOS adaptation**: Always set non-interaction env vars for network operations. Skip network calls when local state is sufficient.

**Pattern: gh CLI timeout**

- **File**: `src/src/utils/ghPrStatus.ts:19`
- **How it works**: `GH_TIMEOUT_MS = 5000` — all `gh` commands have a 5-second timeout
- **Why**: Network issues can cause `gh` to hang. Timeout ensures the UI remains responsive.
- **AgentOS adaptation**: Always set timeouts for network-dependent CLI operations.

### Merge Conflicts

**Pattern: Transient git state detection**

- **File**: `src/src/utils/gitDiff.ts:307-326`
- **How it works**:
  1. Checks for `MERGE_HEAD`, `REBASE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD` files in git dir
  2. Uses `fs.access` (no subprocess) for fast detection
  3. If in transient state, returns `null` for diff operations
  4. Same check in `commitAttribution.ts:843-867` with additional `rebase-merge`, `rebase-apply`, `BISECT_LOG`
- **Why**: During merge/rebase/cherry-pick/revert, the working tree contains incoming changes that weren't intentionally made by the user. Showing diffs would be misleading.
- **AgentOS adaptation**: Detect transient states and skip operations that would produce misleading results.

**Pattern: Merge conflict handling in PR creation**

- **File**: `src/src/commands/commit-push-pr.ts:61-65`
- **How it works**:
  1. Prompt includes `git diff <defaultBranch>...HEAD` which shows all changes since branch diverged
  2. If there are merge conflicts, the diff will show conflict markers
  3. Model is instructed to analyze ALL commits in the PR, not just the latest
- **Why**: The model can see conflict markers in the diff and handle them appropriately (resolve conflicts before committing).
- **AgentOS adaptation**: Include full branch diff in prompts so the model can see and resolve conflicts.

---

## Key Architectural Patterns Summary

| Pattern | File(s) | Purpose |
|---------|---------|---------|
| Memoized binary resolution | `git.ts:212-216` | Avoid repeated PATH lookups |
| `--no-optional-locks` | `git.ts:359`, `gitDiff.ts:64` | Prevent lock conflicts with concurrent git |
| LRU-memoized directory walks | `git.ts:27-86` | Cache git root discovery |
| Cascading fallbacks | `git.ts:562-603` | Maximize compatibility across repo configs |
| Non-interaction env vars | `worktree.ts:195-202` | Prevent hanging credential prompts |
| Fail-closed cleanup | `worktree.ts:1098-1118` | Never delete uncertain state |
| Character-level attribution | `commitAttribution.ts:324-380` | Accurate contribution tracking |
| Prefix/suffix diff matching | `commitAttribution.ts:347-364` | Handle same-length replacements |
| Slug flattening | `worktree.ts:217-219` | Prevent D/F conflicts in git refs |
| Safe-default undercover | `undercover.ts:28-37` | Prevent info leaks by default |
| Build-time constant folding | `undercover.ts:18-21` | Remove undercover code from external builds |
| HEREDOC for multiline args | `commit.ts:48-52`, `commit-push-pr.ts:84-100` | Safe shell escaping |
| Quick probe before expensive ops | `gitDiff.ts:62-79` | Avoid loading massive diffs |
| Filesystem reads over subprocess | `git/gitFilesystem.js` imports | <1ms vs ~15ms per operation |
| Pattern-based orphan cleanup | `worktree.ts:1030-1041` | Clean leaked resources without touching user data |
| Idempotent config writes | `worktree.ts:556-561` | Skip subprocess when value already matches |
| Double error handling | `worktree.ts:606-623` | Handle both module load and operation failures |
| Path traversal validation | `worktree.ts:66-87` | Prevent directory escape via worktree slugs |
| NFC path normalization | `git.ts:48`, `git.ts:71` | macOS symlink compatibility |
| Teardown on partial failure | `worktree.ts:341-348` | Clean up partially created worktrees |
