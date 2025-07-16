#!/bin/bash

# Lazarus Home Remodeling Website - Git Publishing Script
# Automated publishing to GitHub repository: https://github.com/1genadam/lazarus

echo "🏠 Publishing Lazarus Home Remodeling Website to GitHub..."

# Set GitHub repository URL
GITHUB_REPO="https://github.com/1genadam/lazarus"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git remote add origin $GITHUB_REPO
    echo "✅ Git repository initialized"
fi

# Check if remote origin exists and update it
if git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Updating remote origin to: $GITHUB_REPO"
    git remote set-url origin $GITHUB_REPO
else
    echo "🔗 Adding remote origin: $GITHUB_REPO"
    git remote add origin $GITHUB_REPO
fi

# Check current git status
echo "📋 Checking git status..."
git status --porcelain > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Git repository is ready"
else
    echo "❌ Git repository error"
    exit 1
fi

# Add all files to staging
echo "📁 Adding all files to staging..."
git add -A

# Check if there are changes to commit
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "📝 Creating commit with timestamp..."
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    git commit -m "Lazarus Home Remodeling Website Update - $TIMESTAMP

🏠 Website Features:
- Responsive design with Tailwind CSS
- Modern home remodeling service showcase
- Professional navigation and layout
- Before/after gallery sections
- Client testimonials
- Service pages: Kitchen, Bathroom, Whole Home, Exterior
- Contact integration and quote system

🚀 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>" --quiet
    
    echo "✅ Commit created successfully"
else
    echo "ℹ️  No changes to commit"
fi

# Push to GitHub repository
echo "🚀 Pushing to GitHub repository..."
git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null || {
    echo "📤 Creating main branch and pushing..."
    git checkout -b main 2>/dev/null || git checkout main
    git push -u origin main
}

# Check if push was successful
if [ $? -eq 0 ]; then
    echo "✅ Successfully published to GitHub!"
    echo ""
    echo "🌟 LAZARUS HOME REMODELING WEBSITE PUBLISHED:"
    echo "   🔗 Repository: $GITHUB_REPO"
    echo "   📁 Files published:"
    echo "      - public/index.html (Landing page)"
    echo "      - public/services.html (Services showcase)"
    echo "      - README.md (Documentation)"
    echo "      - Docker configuration files"
    echo "      - This publishing script"
    echo ""
    echo "🚀 DEPLOYMENT OPTIONS:"
    echo "   1. GitHub Pages: Enable in repository settings"
    echo "   2. Fly.io: Use included fly.toml configuration"
    echo "   3. Docker: Use included Dockerfile"
    echo "   4. Static hosting: Upload public/ directory"
    echo ""
    echo "📖 Next Steps:"
    echo "   - Visit repository to configure GitHub Pages"
    echo "   - Review deployment options in README.md"
    echo "   - Customize content for specific client needs"
    echo "   - Add additional pages (portfolio, about, contact)"
    exit 0
else
    echo "❌ Failed to push to GitHub"
    echo "📋 Troubleshooting:"
    echo "   - Check GitHub authentication (git config --global user.name/email)"
    echo "   - Verify repository exists: $GITHUB_REPO"
    echo "   - Check network connection"
    echo "   - Try running: git push --verbose"
    exit 1
fi