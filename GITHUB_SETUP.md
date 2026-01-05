# 🚀 GitHub Setup Guide

This guide will help you push Open Pandas-AI to GitHub.

## 📋 Prerequisites

- Git installed and configured
- GitHub account
- Repository created on GitHub (or we'll create one)

## 🔧 Step-by-Step Instructions

### 1. Check Current Git Status

```powershell
git status
```

### 2. Add All Files

```powershell
git add .
```

### 3. Commit Changes

```powershell
git commit -m "Initial commit: Add Open Pandas-AI v2.0 with documentation"
```

Or use the interactive script:

```powershell
.\push_to_github.ps1
```

### 4. Set Remote Repository (if not already set)

If you haven't created a GitHub repository yet:

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `Open_Pandas_AI` (or your preferred name)
3. **Don't** initialize with README, .gitignore, or license (we already have them)

Then add the remote:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/Open_Pandas_AI.git
```

Or if using SSH:

```powershell
git remote add origin git@github.com:YOUR_USERNAME/Open_Pandas_AI.git
```

### 5. Verify Remote

```powershell
git remote -v
```

### 6. Push to GitHub

```powershell
git push -u origin main
```

If your default branch is `master`:

```powershell
git push -u origin master
```

## 📝 Files Included

The following files will be pushed:

- ✅ `README.md` - Updated with GitHub badges and documentation
- ✅ `TECHNICAL_REPORT.md` - Complete technical documentation
- ✅ `LICENSE` - MIT License
- ✅ `.gitignore` - Enhanced Python/Streamlit gitignore
- ✅ `CONTRIBUTING.md` - Contribution guidelines
- ✅ `.github/` - Issue templates, PR template, CI workflow
- ✅ All source code files

## 🔒 Important: Environment Variables

**DO NOT** commit `.env` files! They are already in `.gitignore`.

Create a `.env.example` file for reference:

```env
# LLM Configuration
MISTRAL_API_KEY=your-api-key-here
LLM_PROVIDER=codestral
LLM_MODEL=codestral-latest

# Docker Sandbox
USE_DOCKER_SANDBOX=false
SANDBOX_TIMEOUT_SECONDS=30

# Database (optional)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/openpanda

# Ollama (if using)
OLLAMA_BASE_URL=http://localhost:11434

# LM Studio (if using)
LMSTUDIO_BASE_URL=http://localhost:1234
```

## 🎯 Quick Push Script

Use the provided PowerShell script:

```powershell
.\push_to_github.ps1
```

This script will:
1. Check git status
2. Add all files
3. Ask for commit message
4. Commit changes
5. Ask to push
6. Push to GitHub

## 🔄 Updating the Repository

After making changes:

```powershell
git add .
git commit -m "Your commit message"
git push
```

## 📚 Next Steps After Push

1. **Add repository description** on GitHub
2. **Add topics/tags**: `python`, `streamlit`, `ai`, `data-analysis`, `pandas`, `llm`
3. **Enable GitHub Actions** (if using CI/CD)
4. **Add README badges** (update URLs in README.md with your repo URL)
5. **Create releases** for version tags

## 🐛 Troubleshooting

### Authentication Issues

If you get authentication errors:

**Option 1: Use Personal Access Token**
```powershell
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/Open_Pandas_AI.git
```

**Option 2: Use SSH**
```powershell
git remote set-url origin git@github.com:YOUR_USERNAME/Open_Pandas_AI.git
```

### Branch Name Issues

If your default branch is `master` instead of `main`:

```powershell
git branch -M main
git push -u origin main
```

## ✅ Verification

After pushing, verify on GitHub:
- [ ] README.md displays correctly
- [ ] All files are present
- [ ] LICENSE file is recognized
- [ ] .github templates work
- [ ] No sensitive files (.env) are committed

---

**Need help?** Open an issue or check the [GitHub documentation](https://docs.github.com/).
