#!/usr/bin/env bash

set -euo pipefail

SOURCE_BRANCH="redesign/react-fastapi"
GITHUB_URL="https://github.com/ckakalou/SDoH_Screener.git"
HUGGING_FACE_URL="https://huggingface.co/spaces/ckakalou/Healie_SDoHScreener"

SCRIPT_DIRECTORY="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1
  pwd
)"

DEFAULT_SOURCE_REPOSITORY="$(
  cd -- "$SCRIPT_DIRECTORY/.." >/dev/null 2>&1
  pwd
)"

SOURCE_REPOSITORY="${1:-$DEFAULT_SOURCE_REPOSITORY}"
DEPLOYMENT_REPOSITORY="${2:-$(dirname "$SOURCE_REPOSITORY")/SDoH_Screener_HF_Deploy}"

EXCLUDED_PNG_FILES=(
  "frontend/public/healie-favicon.png"
  "frontend/public/healie_final_official_logo_full.png"
  "frontend/public/healie_final_official_logo_trans_crop.png"
  "frontend/src/assets/hero.png"
  "sdoh_favicon.png"
)

fail() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

run_git() {
  local repository="$1"
  shift

  git -C "$repository" "$@"
}

if [[ ! -d "$SOURCE_REPOSITORY/.git" ]]; then
  fail "Source repository was not found at $SOURCE_REPOSITORY"
fi

if [[ ! -d "$DEPLOYMENT_REPOSITORY/.git" ]]; then
  fail "Hugging Face deployment repository was not found at $DEPLOYMENT_REPOSITORY"
fi

if [[ -n "$(git -C "$SOURCE_REPOSITORY" status --porcelain)" ]]; then
  fail "The source repository has uncommitted changes. Commit them before deploying."
fi

CURRENT_BRANCH="$(git -C "$SOURCE_REPOSITORY" branch --show-current)"

if [[ "$CURRENT_BRANCH" != "$SOURCE_BRANCH" ]]; then
  fail "The source repository must be on $SOURCE_BRANCH. Current branch: $CURRENT_BRANCH"
fi

printf 'Checking the GitHub source branch...\n'
run_git "$SOURCE_REPOSITORY" fetch origin "$SOURCE_BRANCH"

SOURCE_HEAD="$(git -C "$SOURCE_REPOSITORY" rev-parse HEAD)"
GITHUB_HEAD="$(git -C "$SOURCE_REPOSITORY" rev-parse "origin/$SOURCE_BRANCH")"

if [[ "$SOURCE_HEAD" != "$GITHUB_HEAD" ]]; then
  fail "The source branch is not synchronized with GitHub. Push or pull before deploying."
fi

if [[ -n "$(git -C "$DEPLOYMENT_REPOSITORY" status --porcelain)" ]]; then
  fail "The Hugging Face deployment repository has uncommitted changes."
fi

if git -C "$DEPLOYMENT_REPOSITORY" remote | grep -Fxq "hf"; then
  HF_REMOTE="$(git -C "$DEPLOYMENT_REPOSITORY" remote get-url hf)"

  if [[ "$HF_REMOTE" != "$HUGGING_FACE_URL" ]]; then
    fail "The deployment repository's hf remote points to an unexpected URL: $HF_REMOTE"
  fi
else
  run_git "$DEPLOYMENT_REPOSITORY" remote add hf "$HUGGING_FACE_URL"
fi

if git -C "$DEPLOYMENT_REPOSITORY" remote | grep -Fxq "source"; then
  SOURCE_REMOTE="$(git -C "$DEPLOYMENT_REPOSITORY" remote get-url source)"

  if [[ "$SOURCE_REMOTE" != "$GITHUB_URL" ]]; then
    fail "The deployment repository's source remote points to an unexpected URL: $SOURCE_REMOTE"
  fi
else
  run_git "$DEPLOYMENT_REPOSITORY" remote add source "$GITHUB_URL"
fi

DEPLOYMENT_BRANCH="$(
  git -C "$DEPLOYMENT_REPOSITORY" branch --show-current
)"

if [[ "$DEPLOYMENT_BRANCH" != "main" ]]; then
  fail "The deployment repository must be on main. Current branch: $DEPLOYMENT_BRANCH"
fi

printf 'Synchronizing the Hugging Face deployment history...\n'
run_git "$DEPLOYMENT_REPOSITORY" fetch hf main
run_git "$DEPLOYMENT_REPOSITORY" merge --ff-only hf/main

printf 'Fetching the latest GitHub version...\n'
run_git "$DEPLOYMENT_REPOSITORY" fetch source "$SOURCE_BRANCH"

printf 'Synchronizing the deployment snapshot...\n'
run_git \
  "$DEPLOYMENT_REPOSITORY" \
  rm -r --ignore-unmatch .

run_git \
  "$DEPLOYMENT_REPOSITORY" \
  checkout "source/$SOURCE_BRANCH" -- .

for relative_path in "${EXCLUDED_PNG_FILES[@]}"; do
  full_path="$DEPLOYMENT_REPOSITORY/$relative_path"

  if [[ -f "$full_path" ]]; then
    rm -- "$full_path"
  fi
done

run_git "$DEPLOYMENT_REPOSITORY" add -A

REMAINING_PNG_FILES="$(
  find "$DEPLOYMENT_REPOSITORY" \
    \( -type d \( \
      -name ".git" -o \
      -name "node_modules" -o \
      -name "dist" \
    \) -prune \) \
    -o \
    \( -type f -iname "*.png" -print \)
)"

if [[ -n "$REMAINING_PNG_FILES" ]]; then
  printf 'Error: PNG files remain in the deployment snapshot:\n%s\n' \
    "$REMAINING_PNG_FILES" >&2
  exit 1
fi

run_git "$DEPLOYMENT_REPOSITORY" diff --cached --check

if run_git "$DEPLOYMENT_REPOSITORY" diff --cached --quiet; then
  printf 'Hugging Face is already up to date.\n'
  exit 0
fi

SHORT_SOURCE_COMMIT="$(
  git -C "$SOURCE_REPOSITORY" rev-parse --short HEAD
)"

run_git \
  "$DEPLOYMENT_REPOSITORY" \
  commit -m "Deploy GitHub revision $SHORT_SOURCE_COMMIT"

printf 'Pushing the deployment to Hugging Face...\n'
run_git "$DEPLOYMENT_REPOSITORY" push hf main:main

printf 'Deployment pushed successfully.\n'
printf 'https://huggingface.co/spaces/ckakalou/Healie_SDoHScreener\n'