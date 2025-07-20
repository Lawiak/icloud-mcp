# GitHub Upload Instructions

## Step 1: Create Repository on GitHub

1. **Go to GitHub:** https://github.com/new
2. **Repository name:** `icloud-mcp`
3. **Description:** `iCloud Email MCP Server - AI assistant email integration with Docker and Raspberry Pi support`
4. **Visibility:** Public (recommended so others can benefit)
5. **Initialize:** 
   - ❌ Don't add README.md (we already have one)
   - ❌ Don't add .gitignore (we already have one)
   - ❌ Don't choose a license yet
6. **Click:** "Create repository"

## Step 2: Upload Your Code

After creating the repository, GitHub will show you commands. Use these:

```bash
# Navigate to your project
cd /Users/lawiak/data/claude/icloud-mcp-server

# Add your GitHub repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/icloud-mcp.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify Upload

1. **Check your repository:** https://github.com/YOUR_USERNAME/icloud-mcp
2. **Verify files are there:**
   - README.md should display the project description
   - All 15 files should be visible
   - .env.example should show safe placeholder values

## Step 4: Optional Enhancements

1. **Add Topics/Tags:**
   - Go to your repository settings
   - Add topics: `mcp`, `icloud`, `email`, `docker`, `raspberry-pi`, `claude`, `ai`

2. **Add a License:**
   - Click "Add file" → "Create new file"
   - Name: `LICENSE`
   - Choose MIT License (recommended for open source)

3. **Create Releases:**
   - Go to "Releases" → "Create a new release"
   - Tag: `v1.0.0`
   - Title: `Initial Release - iCloud Email MCP Server`

## Troubleshooting

**If you get authentication errors:**
- Use a Personal Access Token instead of password
- Go to GitHub Settings → Developer settings → Personal access tokens
- Generate a token with `repo` permissions

**If remote already exists:**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/icloud-mcp.git
```

## Security Note

✅ **Safe to upload:** All sensitive credentials have been removed
✅ **Protected:** .gitignore prevents future credential commits
✅ **Example values:** Only placeholder values remain in the code