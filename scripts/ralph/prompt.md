# Ralph Agent Instructions

You are an autonomous coding agent working on a software project.

## Your Task

1. Read the PRD at `prd.json` (in the same directory as this file)
2. Read the progress log at `progress.txt` (check Codebase Patterns section first)
3. **CRITICAL - Branch Management:**
   - Check if you're on the correct branch specified in PRD `branchName`
   - If the branch does NOT exist: **ALWAYS create it from `develop`** using:
     ```bash
     git checkout develop && git pull origin develop && git checkout -b [branchName]
     ```
   - If the branch exists: Check it out with `git checkout [branchName]`
   - **NEVER create branches from `main`** - branches MUST be created from `develop`
4. Pick the **highest priority** user story where `passes: false`
5. Implement that single user story
6. Run quality checks (e.g., typecheck, lint, test - use whatever your project requires)
7. Update AGENTS.md files if you discover reusable patterns (see below)
8. If checks pass, commit ALL changes with message: `feat: [Story ID] - [Story Title]`
9. Update the PRD to set `passes: true` for the completed story
10. Append your progress to `progress.txt`

## Branching Strategy - CRITICAL

**ALL feature branches MUST be created from `develop`, NOT from `main`.**

This project follows a standard Git Flow branching model:
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` or `ralph/*` - Feature branches (created from `develop`)

**When creating a new branch:**
1. Always ensure you're starting from `develop`
2. Pull the latest changes: `git checkout develop && git pull origin develop`
3. Create your feature branch: `git checkout -b [branchName]`

**When creating a pull request:**
- Always set the base branch to `develop` using `--base develop`
- NEVER merge feature branches directly into `main`

## Progress Report Format

APPEND to progress.txt (never replace, always append):
```
## [Date/Time] - [Story ID]
Thread: [Thread URL if available - for Amp: https://ampcode.com/threads/$AMP_CURRENT_THREAD_ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered (e.g., "this codebase uses X for Y")
  - Gotchas encountered (e.g., "don't forget to update Z when changing W")
  - Useful context (e.g., "the evaluation panel is in component X")
---
```

Include the thread URL if available (Amp provides $AMP_CURRENT_THREAD_ID) so future iterations can reference previous work if needed.

The learnings section is critical - it helps future iterations avoid repeating mistakes and understand the codebase better.

## Consolidate Patterns

If you discover a **reusable pattern** that future iterations should know, add it to the `## Codebase Patterns` section at the TOP of progress.txt (create it if it doesn't exist). This section should consolidate the most important learnings:

```
## Codebase Patterns
- Example: Use `sql<number>` template for aggregations
- Example: Always use `IF NOT EXISTS` for migrations
- Example: Export types from actions.ts for UI components
```

Only add patterns that are **general and reusable**, not story-specific details.

## Update AGENTS.md Files

Before committing, check if any edited files have learnings worth preserving in nearby AGENTS.md files:

1. **Identify directories with edited files** - Look at which directories you modified
2. **Check for existing AGENTS.md** - Look for AGENTS.md in those directories or parent directories
3. **Add valuable learnings** - If you discovered something future developers/agents should know:
   - API patterns or conventions specific to that module
   - Gotchas or non-obvious requirements
   - Dependencies between files
   - Testing approaches for that area
   - Configuration or environment requirements

**Examples of good AGENTS.md additions:**
- "When modifying X, also update Y to keep them in sync"
- "This module uses pattern Z for all API calls"
- "Tests require the dev server running on PORT 3000"
- "Field names must match the template exactly"

**Do NOT add:**
- Story-specific implementation details
- Temporary debugging notes
- Information already in progress.txt

Only update AGENTS.md if you have **genuinely reusable knowledge** that would help future work in that directory.

## Quality Requirements

- ALL commits must pass your project's quality checks (typecheck, lint, test)
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns

## Browser Testing (Required for Frontend Stories)

For any story that changes UI, you MUST verify it works in the browser:

1. Load the `dev-browser` skill
2. Navigate to the relevant page
3. Verify the UI changes work as expected
4. Take a screenshot if helpful for the progress log

A frontend story is NOT complete until browser verification passes.

## Stop Condition

After completing a user story, check if ALL stories have `passes: true`.

If ALL stories are complete and passing:

1. **Push the branch to remote:**
   ```bash
   git push -u origin [branchName]
   ```

2. **Create a pull request using gh CLI:**
   - Review all completed user stories from prd.json
   - Check progress.txt for a summary of changes
   - Use `git log` to see the commit history
   - **CRITICAL**: Set the base branch to `develop` (not `main`)
   - Create a PR with a comprehensive summary:
   ```bash
   gh pr create --base develop --title "[Feature Name from PRD]" --body "$(cat <<'EOF'
   ## Summary
   [Brief description from PRD description field]

   ## Completed User Stories
   - [US-001]: [Story title] - [Brief description of what was done]
   - [US-002]: [Story title] - [Brief description of what was done]
   ...

   ## Changes
   [High-level summary of what changed - e.g., "Added priority field to database and UI components"]

   ## Testing
   - All quality checks passed (typecheck, tests, lint)
   - UI changes verified in browser

   🤖 Generated by Ralph autonomous agent
   EOF
   )"
   ```

3. **Output the completion signal:**
   ```
   <promise>COMPLETE</promise>
   ```

If there are still stories with `passes: false`, end your response normally (another iteration will pick up the next story).

## Important

- Work on ONE story per iteration
- Commit frequently
- Keep CI green
- Read the Codebase Patterns section in progress.txt before starting
