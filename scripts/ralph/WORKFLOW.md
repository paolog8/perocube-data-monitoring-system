# Ralph Workflow Guide

Complete guide from feature idea to merged code using Ralph's autonomous loop.

## Overview

Ralph automates feature development through an autonomous loop:
1. **Plan** - Create PRD with user stories
2. **Convert** - Transform PRD into `prd.json` task list
3. **Execute** - Ralph implements stories one by one
4. **Review** - Ralph creates PR when complete

Each iteration is a fresh agent instance. Memory persists through git commits, `prd.json` status, and `progress.txt` learnings.

---

## Complete Workflow

### Phase 1: Planning Your Feature

#### Step 1: Start with Your Idea

Think about what you want to build. Examples:
- "Add user profile page with avatar upload"
- "Implement task filtering by priority"
- "Add email notifications for task updates"

**Key considerations:**
- What problem does this solve?
- What should the user experience be?
- What parts of the codebase will this touch?

#### Step 2: Generate a PRD

Use the PRD skill to create a structured requirements document.

**Using Claude Code:**
```bash
claude
```
Then in the conversation:
```
Use the prd skill to create a PRD for: [describe your feature]
```

**Using Amp:**
```bash
amp
```
Then:
```
Use the prd skill to create a PRD for: [describe your feature]
```

**What happens:**
1. Agent asks 3-5 clarifying questions with lettered options
2. You respond with answers (e.g., "1A, 2C, 3B")
3. Agent generates PRD with:
   - User stories (small, completable tasks)
   - Acceptance criteria for each story
   - Priority ordering (database → backend → UI)
4. Saves to `tasks/prd-[feature-name].md`

**Example PRD structure:**
```markdown
# Feature: User Profile Page

## User Stories

### US-001: Create User Profile Schema
**Description:** As a developer, I want a user profile table so that we can store user data.
**Acceptance Criteria:**
- [ ] Create `profiles` table with: user_id, avatar_url, bio, created_at
- [ ] Generate and run migration
- [ ] npm run typecheck passes

### US-002: Add Profile API Endpoints
**Description:** As a developer, I want API endpoints so the frontend can fetch/update profiles.
**Acceptance Criteria:**
- [ ] GET /api/profile/:userId returns profile data
- [ ] PATCH /api/profile/:userId updates profile
- [ ] Tests pass for both endpoints
- [ ] npm run typecheck passes

### US-003: Build Profile UI Component
**Description:** As a user, I want to view and edit my profile so that I can customize my account.
**Acceptance Criteria:**
- [ ] Profile page displays user avatar, name, bio
- [ ] Edit button allows updating bio
- [ ] Changes save via API call
- [ ] npm run typecheck passes
- [ ] Verify in browser using dev-browser skill
```

**PRD Tips:**
- **Keep stories small** - Each should complete in one agent iteration (~10-20 minutes)
- **Order by dependencies** - Database schema first, then API, then UI
- **Be specific in acceptance criteria** - "Button shows confirmation dialog" not "Works correctly"
- **Always include** "npm run typecheck passes" (or your project's quality check)
- **UI stories must include** "Verify in browser using dev-browser skill"

#### Step 3: Convert PRD to prd.json

Use the Ralph skill to convert your markdown PRD into the JSON format Ralph uses.

**In Claude or Amp:**
```
Use the ralph skill to convert tasks/prd-user-profile.md to prd.json
```

**What happens:**
1. Agent reads your PRD
2. Converts user stories to JSON format
3. Asks where to save `prd.json` (should be same directory as `ralph.sh`)
4. Saves `prd.json` with:
   - All stories with `passes: false`
   - Priority ordering
   - Branch name (e.g., `ralph/user-profile`)

**Example prd.json:**
```json
{
  "project": "My App",
  "branchName": "ralph/user-profile",
  "description": "Add user profile page with avatar upload",
  "userStories": [
    {
      "id": "US-001",
      "title": "Create User Profile Schema",
      "description": "As a developer, I want a user profile table...",
      "acceptanceCriteria": [
        "Create profiles table with: user_id, avatar_url, bio, created_at",
        "Generate and run migration",
        "npm run typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-002",
      "title": "Add Profile API Endpoints",
      "description": "As a developer, I want API endpoints...",
      "acceptanceCriteria": [
        "GET /api/profile/:userId returns profile data",
        "PATCH /api/profile/:userId updates profile",
        "Tests pass for both endpoints",
        "npm run typecheck passes"
      ],
      "priority": 2,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### Phase 2: Setting Up Ralph in Your Project

#### Step 4: Install Ralph (First Time Only)

If you haven't already set up Ralph in your project:

```bash
# From the ralph repository
cd /home/qkg/Documents/2_AREAS/tools/ralph

# Copy to your project
mkdir -p /path/to/your-project/scripts/ralph
cp ralph.sh /path/to/your-project/scripts/ralph/
cp prompt.md /path/to/your-project/scripts/ralph/
chmod +x /path/to/your-project/scripts/ralph/ralph.sh
```

#### Step 5: Customize prompt.md (First Time Only)

Edit `scripts/ralph/prompt.md` to match your project's specifics:

```markdown
# Add your project's quality check commands
npm run typecheck
npm run test
npm run lint

# Add project-specific patterns
- Database migrations are in db/migrations/
- API routes use tRPC in src/server/api/
- UI components are in src/components/
```

**Important customizations:**
- Quality check commands (typecheck, tests, lint)
- File structure patterns
- Technology stack specifics
- Common gotchas in your codebase

#### Step 6: Move prd.json to Ralph Directory

```bash
# Move prd.json to where ralph.sh is located
mv prd.json /path/to/your-project/scripts/ralph/
cd /path/to/your-project/scripts/ralph/
```

Ralph expects `prd.json` in the same directory as `ralph.sh`.

### Phase 3: Running Ralph

#### Step 7: Choose Your Agent

Ralph supports four agents. Choose based on your needs:

**Claude Code** (Recommended for complex features):
- Uses Opus Plan model
- Best reasoning and planning
- Extended context window
- Command: `./ralph.sh claude`

**Amp**:
- Fast iterations
- Good for straightforward tasks
- Auto-handoff on context overflow
- Command: `./ralph.sh amp`

**Gemini**:
- Fast and cost-effective
- Good for simpler features
- Command: `./ralph.sh gemini`

**OpenCode**:
- 75+ model providers
- Most flexible
- Command: `./ralph.sh opencode`
- With specific model: `./ralph.sh opencode 10 anthropic/claude-sonnet-4-20250514`

#### Step 8: Run Ralph

```bash
cd /path/to/your-project/scripts/ralph

# Run with your chosen agent (10 iterations max by default)
./ralph.sh claude

# Or specify max iterations
./ralph.sh claude 5

# Or use a different agent
./ralph.sh amp
./ralph.sh gemini
./ralph.sh opencode
```

**What Ralph does each iteration:**
1. Reads `prd.json` and `progress.txt`
2. Checks out/creates branch from `develop` (using `branchName` from prd.json)
3. Picks highest priority story where `passes: false`
4. Implements that story
5. Runs quality checks (typecheck, tests, etc.)
6. If checks pass:
   - Commits with message: `feat: [Story ID] - [Story Title]`
   - Updates `prd.json` to mark `passes: true`
   - Appends learnings to `progress.txt`
7. If all stories pass:
   - Pushes branch to remote
   - Creates PR to `develop` branch
   - Outputs `<promise>COMPLETE</promise>`
   - Loop exits

**If checks fail:**
- Agent attempts to fix issues
- Continues until checks pass or iteration limit reached
- Does NOT commit broken code

### Phase 4: Monitoring Progress

#### Step 9: Watch Ralph Work

Ralph outputs progress in real-time. You'll see:
- Which story it's working on
- File changes being made
- Quality check results
- Commit messages
- Learnings being added to progress.txt

**Monitor in another terminal:**
```bash
# Watch which stories are complete
watch -n 5 'cat prd.json | jq ".userStories[] | {id, title, passes}"'

# Follow progress learnings
tail -f progress.txt

# Watch git commits
watch -n 5 'git log --oneline -10'
```

#### Step 10: Handle Issues

**If Ralph gets stuck:**
- Check the current story's acceptance criteria
- Look at `progress.txt` for learnings
- Review quality check errors
- Consider if the story is too large (needs splitting)

**If you need to intervene:**
```bash
# Kill Ralph (Ctrl+C in the terminal)
^C

# Fix the issue manually
git add .
git commit -m "fix: [description]"

# Update prd.json manually if needed (mark story as passes: true)
# Or continue from where it left off
./ralph.sh claude
```

**If quality checks keep failing:**
- Story might be too complex (split it)
- Acceptance criteria might be unclear
- Project-specific patterns might need documentation in `prompt.md`

### Phase 5: Review and Merge

#### Step 11: Review the Pull Request

When Ralph completes all stories, it:
1. Pushes branch to remote
2. Creates PR to `develop` branch with summary:
   ```markdown
   # Feature: User Profile Page

   ## Completed Stories
   - ✅ US-001: Create User Profile Schema
   - ✅ US-002: Add Profile API Endpoints
   - ✅ US-003: Build Profile UI Component

   ## Changes
   - Added profiles table migration
   - Implemented GET and PATCH endpoints for profiles
   - Created ProfilePage component with edit functionality

   ## Testing
   All acceptance criteria verified:
   - Database schema created and migrated
   - API endpoints tested and passing
   - UI verified in browser
   - All quality checks passing
   ```

**Review checklist:**
- [ ] All commits follow proper format
- [ ] Quality checks are passing in CI
- [ ] Code follows project patterns
- [ ] Acceptance criteria are met
- [ ] No unnecessary changes or files
- [ ] AGENTS.md updated with learnings

#### Step 12: Test the Feature

```bash
# Check out the branch
git fetch origin
git checkout ralph/user-profile

# Run the app
npm run dev

# Test the feature manually
# - Navigate to the profile page
# - Try editing the profile
# - Verify changes save correctly

# Run full test suite
npm run test
npm run typecheck
npm run lint
```

#### Step 13: Merge

If everything looks good:
```bash
# Via GitHub UI: Click "Merge Pull Request"
# Or via CLI:
gh pr merge --merge  # or --squash or --rebase based on your workflow
```

The feature branch merges into `develop`, ready for eventual release.

---

## Tips for Success

### Story Sizing

**Too large (will fail):**
- "Build entire authentication system"
- "Create admin dashboard"
- "Implement search with filters, sorting, and pagination"

**Right size (will succeed):**
- "Add password reset endpoint"
- "Create login form component"
- "Add search by title to task list"

**Rule of thumb:** If the story touches more than 3-4 files or requires more than ~100 lines of code, split it.

### Acceptance Criteria

**Vague (bad):**
- "Works correctly"
- "Looks good"
- "No errors"

**Specific (good):**
- "Button shows confirmation dialog before deleting"
- "Error message displays 'Invalid email format' for malformed emails"
- "npm run typecheck passes with no errors"

### Story Dependencies

Order stories so each one builds on previous work:

**Correct order:**
1. Database schema
2. Backend API
3. Frontend UI
4. UI enhancements

**Wrong order:**
1. Frontend UI (needs API, which needs schema)
2. Database schema (UI already expects it)
3. Backend API (too late)

### Quality Checks

Ralph only commits code that passes checks. Define these in `prompt.md`:

**Essential (always include):**
```bash
npm run typecheck  # or tsc --noEmit
```

**Recommended:**
```bash
npm run test       # unit and integration tests
npm run lint       # eslint, prettier
npm run build      # ensure builds succeed
```

**For specific stories:**
```bash
# For database changes
npm run db:validate

# For UI changes
# Verify in browser using dev-browser skill (in acceptance criteria)
```

### Browser Verification

For UI stories, Ralph uses the dev-browser skill to visually verify changes:

**In acceptance criteria, include:**
```
- [ ] Verify in browser using dev-browser skill
```

**Ralph will:**
1. Start dev-browser server
2. Navigate to the relevant page
3. Take screenshots
4. Verify visual appearance
5. Test interactions (clicks, form fills)

### Progress Tracking

Ralph learns and documents as it works:

**progress.txt contains:**
- Patterns discovered: "This codebase uses tRPC for API routes"
- Gotchas avoided: "Must update types.ts when adding new DB columns"
- Useful context: "Settings panel is in src/components/layout/Settings.tsx"

**AGENTS.md updates:**
Future iterations (and human developers) benefit from these learnings.

### Archive Management

Ralph automatically archives previous runs:

```bash
# When you start a new feature with a different branchName:
# Old prd.json, progress.txt moved to:
archive/2026-01-12-old-feature-name/
```

This keeps your workspace clean while preserving history.

---

## Common Scenarios

### Scenario 1: Simple Feature (1-3 stories)

**Example:** Add a "Mark as Complete" button to tasks

```bash
# 1. Generate PRD
claude
> Use the prd skill for: Add mark as complete button to tasks

# Answer questions, PRD created in tasks/prd-mark-complete.md

# 2. Convert to prd.json
> Use the ralph skill to convert tasks/prd-mark-complete.md

# 3. Run Ralph
exit  # exit claude
cd scripts/ralph
./ralph.sh claude 5

# 4. Wait 15-30 minutes
# 5. Review PR and merge
```

### Scenario 2: Medium Feature (4-8 stories)

**Example:** Add user profile page

```bash
# 1. Generate PRD (20-30 min conversation)
claude
> Use the prd skill for: Add user profile page with avatar upload

# 2. Convert to prd.json
> Use the ralph skill to convert tasks/prd-user-profile.md

# 3. Run Ralph
exit
cd scripts/ralph
./ralph.sh claude

# 4. Wait 1-2 hours
# 5. Review PR and merge
```

### Scenario 3: Large Feature (9+ stories)

**Example:** Add team collaboration features

```bash
# 1. Generate PRD (may take multiple conversations)
claude
> Use the prd skill for: Add team collaboration with invites and permissions

# PRD might be large - consider splitting into multiple features

# 2. Review PRD and consider splitting
# If stories are too coupled, keep together
# If stories are independent, create multiple PRDs

# 3. Convert to prd.json
> Use the ralph skill to convert tasks/prd-team-collaboration.md

# 4. Run Ralph with more iterations
exit
cd scripts/ralph
./ralph.sh claude 20

# 5. Monitor closely, may need intervention
# 6. Review PR carefully
# 7. Merge when satisfied
```

### Scenario 4: Ralph Gets Stuck

**Problem:** Story fails quality checks repeatedly

```bash
# 1. Stop Ralph
Ctrl+C

# 2. Investigate
cat progress.txt  # See what was attempted
git diff          # See current changes
npm run typecheck # Run checks manually

# 3. Fix the issue
# Option A: Fix manually and commit
git add .
git commit -m "fix: resolve type errors in profile schema"

# Option B: Update prd.json to split the story
# Edit prd.json, split complex story into 2 smaller ones

# Option C: Update prompt.md with learnings
# Add project-specific patterns Ralph should know

# 4. Update prd.json
# Mark fixed story as passes: true if manually completed

# 5. Restart Ralph
./ralph.sh claude
```

### Scenario 5: Testing Locally Before Ralph

**You want to validate your PRD before running Ralph:**

```bash
# 1. Create PRD and prd.json as usual

# 2. Manually implement first story to test workflow
git checkout develop
git pull origin develop
git checkout -b ralph/feature-test
# ... implement first story ...
npm run typecheck
git add .
git commit -m "feat: US-001 - First Story"

# 3. If workflow is good, reset and let Ralph do it
git checkout develop
git branch -D ralph/feature-test

# 4. Run Ralph
cd scripts/ralph
./ralph.sh claude
```

---

## Troubleshooting

### Ralph Creates Branch from Wrong Base

**Problem:** Branch created from `main` instead of `develop`

**Solution:** Ralph is configured to use `develop`. Check `prompt.md`:
```bash
git checkout develop && git pull origin develop && git checkout -b [branchName]
```

### Stories Complete But No PR Created

**Problem:** All stories have `passes: true` but Ralph didn't create PR

**Solution:** Manually create PR:
```bash
git push -u origin ralph/feature-name
gh pr create --base develop --title "Feature Name" --body "Description"
```

### Quality Checks Pass Locally But Ralph Fails

**Problem:** You can run checks successfully but Ralph reports failures

**Solution:**
- Ensure `prompt.md` has correct check commands
- Verify commands work from Ralph's directory
- Check if commands require environment variables

### Ralph Commits Broken Code

**Problem:** Ralph committed code that doesn't pass checks

**Solution:**
- This shouldn't happen (Ralph only commits passing code)
- If it does, it's a bug in Ralph's logic
- Fix manually:
  ```bash
  git revert HEAD
  # Fix the issue
  git add .
  git commit -m "fix: correct previous commit"
  ```

### prd.json Gets Corrupted

**Problem:** `prd.json` has syntax errors after Ralph update

**Solution:**
```bash
# Restore from git
git checkout scripts/ralph/prd.json

# Or manually fix JSON syntax
# Use jq to validate:
cat prd.json | jq .
```

### Agent Runs Out of Context

**Problem:** Story too large, agent hits context limit mid-implementation

**Solution:**
- Split the story into smaller pieces
- Update prd.json with multiple smaller stories
- For Amp: Enable auto-handoff in `~/.amp/settings.json`:
  ```json
  { "amp.experimental.autoHandoff": { "context": 90 } }
  ```

---

## Best Practices

### 1. Start Small

First time using Ralph? Start with a 1-2 story feature to learn the workflow.

### 2. Customize prompt.md

Spend time making `prompt.md` specific to your project:
- Exact quality check commands
- File structure patterns
- Common mistakes to avoid
- Technology-specific patterns

### 3. Monitor First Few Iterations

Don't walk away immediately. Watch Ralph's first 2-3 iterations to ensure:
- It's picking the right stories
- It's implementing correctly
- Quality checks are working
- Commits are clean

### 4. Keep Stories Independent

Each story should be independently verifiable. Don't make Story 3 depend on Story 2 being perfect.

### 5. Update progress.txt Manually

If you learn something Ralph should know, add it to `progress.txt` before running:
```bash
echo "IMPORTANT: Always update schema.prisma before migrations" >> progress.txt
```

### 6. Review PRs Carefully

Ralph is autonomous but not infallible. Review:
- Code quality and patterns
- Test coverage
- Unnecessary changes
- Security implications

### 7. Iterate on PRD Quality

Your first PRDs won't be perfect. Learn from each Ralph run:
- Were stories sized right?
- Were acceptance criteria clear?
- Was ordering correct?

Improve your PRD skill over time.

---

## Next Steps

Now that you understand the workflow:

1. **Try it** - Start with a small feature in a test project
2. **Customize** - Update `prompt.md` for your specific project
3. **Iterate** - Learn from each Ralph run and improve PRDs
4. **Scale** - Once comfortable, use Ralph for larger features

Ralph works best when:
- ✅ Stories are small and clear
- ✅ Acceptance criteria are specific
- ✅ Quality checks are comprehensive
- ✅ prompt.md is project-specific

Happy autonomous coding! 🤖
