#!/bin/bash
# Ralph Wiggum - Long-running AI agent loop
# Usage: ./ralph.sh <agent> [max_iterations] [model]
#   agent: "amp", "claude", "gemini", or "opencode"
#   max_iterations: number of iterations (default: 10)
#   model: provider/model for opencode only (optional)

set -e

# Help function
show_help() {
  cat << 'EOF'
Ralph Wiggum - Long-running AI agent loop

USAGE:
  ./ralph.sh <agent> [max_iterations] [model]

ARGUMENTS:
  agent           Required. One of: amp, claude, gemini, opencode
  max_iterations  Optional. Number of iterations (default: 10)
  model           Optional. For opencode only: provider/model format

EXAMPLES:
  ./ralph.sh amp                    # Run with Amp, 10 iterations
  ./ralph.sh claude 5               # Run with Claude Code, 5 iterations
  ./ralph.sh gemini                 # Run with Gemini CLI, 10 iterations
  ./ralph.sh opencode               # Run with OpenCode (user's default model)
  ./ralph.sh opencode 10 anthropic/claude-sonnet-4-20250514

AGENT DETAILS:
  amp       Uses: amp --dangerously-allow-all
  claude    Uses: claude --model opusplan --dangerously-skip-permissions
  gemini    Uses: gemini --approval-mode=yolo
  opencode  Uses: opencode run (auto-approves in non-interactive mode)

OPENCODE MODELS:
  OpenCode supports 75+ providers. Format: provider/model

  Common providers:
    anthropic/claude-sonnet-4-20250514
    anthropic/claude-opus-4-20250514
    openai/gpt-4o
    openai/o1
    google/gemini-2.0-flash
    ollama/llama3  (local)

  Run 'opencode models' to list all available models.

  Provider documentation:
    https://opencode.ai/docs/providers/
    https://opencode.ai/docs/models/
EOF
}

# Check for help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  show_help
  exit 0
fi

# Check if agent parameter is provided
if [ -z "$1" ]; then
  echo "Error: Agent parameter is required"
  echo ""
  show_help
  exit 1
fi

AGENT="$1"
MAX_ITERATIONS=${2:-10}
OPENCODE_MODEL="${3:-}"

# Validate agent parameter
if [ "$AGENT" != "amp" ] && [ "$AGENT" != "claude" ] && [ "$AGENT" != "gemini" ] && [ "$AGENT" != "opencode" ]; then
  echo "Error: Invalid agent '$AGENT'"
  echo "Agent must be 'amp', 'claude', 'gemini', or 'opencode'"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$SCRIPT_DIR/prd.json"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"
ARCHIVE_DIR="$SCRIPT_DIR/archive"
LAST_BRANCH_FILE="$SCRIPT_DIR/.last-branch"

# Detect project root (git repository root)
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$PROJECT_ROOT" ]; then
  echo "Error: Not inside a git repository"
  echo "Ralph must be run from within a git repository."
  exit 1
fi

# Archive previous run if branch changed
if [ -f "$PRD_FILE" ] && [ -f "$LAST_BRANCH_FILE" ]; then
  CURRENT_BRANCH=$(jq -r '.branchName // empty' "$PRD_FILE" 2>/dev/null || echo "")
  LAST_BRANCH=$(cat "$LAST_BRANCH_FILE" 2>/dev/null || echo "")
  
  if [ -n "$CURRENT_BRANCH" ] && [ -n "$LAST_BRANCH" ] && [ "$CURRENT_BRANCH" != "$LAST_BRANCH" ]; then
    # Archive the previous run
    DATE=$(date +%Y-%m-%d)
    # Strip "ralph/" prefix from branch name for folder
    FOLDER_NAME=$(echo "$LAST_BRANCH" | sed 's|^ralph/||')
    ARCHIVE_FOLDER="$ARCHIVE_DIR/$DATE-$FOLDER_NAME"
    
    echo "Archiving previous run: $LAST_BRANCH"
    mkdir -p "$ARCHIVE_FOLDER"
    [ -f "$PRD_FILE" ] && cp "$PRD_FILE" "$ARCHIVE_FOLDER/"
    [ -f "$PROGRESS_FILE" ] && cp "$PROGRESS_FILE" "$ARCHIVE_FOLDER/"
    echo "   Archived to: $ARCHIVE_FOLDER"
    
    # Reset progress file for new run
    echo "# Ralph Progress Log" > "$PROGRESS_FILE"
    echo "Started: $(date)" >> "$PROGRESS_FILE"
    echo "---" >> "$PROGRESS_FILE"
  fi
fi

# Track current branch
if [ -f "$PRD_FILE" ]; then
  CURRENT_BRANCH=$(jq -r '.branchName // empty' "$PRD_FILE" 2>/dev/null || echo "")
  if [ -n "$CURRENT_BRANCH" ]; then
    echo "$CURRENT_BRANCH" > "$LAST_BRANCH_FILE"
  fi
fi

# Initialize progress file if it doesn't exist
if [ ! -f "$PROGRESS_FILE" ]; then
  echo "# Ralph Progress Log" > "$PROGRESS_FILE"
  echo "Started: $(date)" >> "$PROGRESS_FILE"
  echo "---" >> "$PROGRESS_FILE"
fi

# Change to project root so agent has access to all project files
cd "$PROJECT_ROOT"

echo "Starting Ralph with $AGENT - Max iterations: $MAX_ITERATIONS"
echo "Project root: $PROJECT_ROOT"

for i in $(seq 1 $MAX_ITERATIONS); do
  echo ""
  echo "═══════════════════════════════════════════════════════"
  echo "  Ralph Iteration $i of $MAX_ITERATIONS (using $AGENT)"
  echo "═══════════════════════════════════════════════════════"

  # Run the appropriate agent with the ralph prompt
  if [ "$AGENT" = "amp" ]; then
    OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | amp --dangerously-allow-all 2>&1 | tee /dev/stderr) || true
  elif [ "$AGENT" = "claude" ]; then
    OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | claude --model opusplan --dangerously-skip-permissions 2>&1 | tee /dev/stderr) || true
  elif [ "$AGENT" = "gemini" ]; then
    OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | gemini --approval-mode=yolo 2>&1 | tee /dev/stderr) || true
  elif [ "$AGENT" = "opencode" ]; then
    if [ -n "$OPENCODE_MODEL" ]; then
      OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | opencode run --model "$OPENCODE_MODEL" 2>&1 | tee /dev/stderr) || true
    else
      OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | opencode run 2>&1 | tee /dev/stderr) || true
    fi
  fi
  
  # Check for completion signal
  if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    echo ""
    echo "Ralph completed all tasks!"
    echo "Completed at iteration $i of $MAX_ITERATIONS"
    exit 0
  fi
  
  echo "Iteration $i complete. Continuing..."
  sleep 2
done

echo ""
echo "Ralph reached max iterations ($MAX_ITERATIONS) without completing all tasks."
echo "Check $PROGRESS_FILE for status."
exit 1
