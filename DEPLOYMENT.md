# HEALIE Screener Deployment

This guide describes how to validate, publish, and deploy changes from the
`redesign/react-fastapi` branch.

## 1. Confirm the correct branch

```bash
git status -sb
git branch --show-current
```

The active branch must be:

```text
redesign/react-fastapi
```

Resolve or preserve any local changes before updating or deploying.

## 2. Run the validation checks

### Windows PowerShell

```powershell
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run lint
npm.cmd --prefix frontend run build
python -m pytest backend/tests -v
git diff --check
```

### macOS or Linux

```bash
npm --prefix frontend test
npm --prefix frontend run lint
npm --prefix frontend run build
python -m pytest backend/tests -v
git diff --check
```

## 3. Commit and push to GitHub

Stage only the files that belong to the change:

```bash
git add <changed-files>
git diff --cached --stat
git diff --cached --check
git commit -m "Describe the change"
git push origin redesign/react-fastapi
```

Confirm that the branch is synchronized:

```bash
git status -sb
git rev-list --left-right --count HEAD...origin/redesign/react-fastapi
```

The comparison should return:

```text
0       0
```

## 4. Deploy to Hugging Face

The deployment scripts require a clean source repository synchronized with
GitHub.

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy-huggingface.ps1
```

### macOS or Linux

```bash
./scripts/deploy-huggingface.sh
```

Both scripts update the clean deployment repository and push the resulting
snapshot to the HEALIE SDoH Screener Hugging Face Space.

## 5. Verify the deployment

Open:

https://huggingface.co/spaces/ckakalou/Healie_SDoHScreener

Confirm that the Space builds successfully and manually test the affected
questionnaire or export behaviour.

## Releases

Ordinary development changes use Git commits. Create a version tag and GitHub
Release only for a coherent, tested milestone that should be reproducible,
deployed, evaluated, shared, or cited.

Do not move or overwrite a published release tag. Corrections after a published
release should use a new patch version.