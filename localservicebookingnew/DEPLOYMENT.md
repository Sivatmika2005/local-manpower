# GitHub Deployment Guide

## Step 1: Initialize Git Repository

Open your terminal/command prompt and navigate to your project folder:

```bash
cd "c:/Users/Admin/Downloads/local serice booking (2) (1)/local serice booking/local serice booking"
```

Initialize Git:
```bash
git init
```

## Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click the "+" icon in the top right and select "New repository"
3. Repository name: `local-service-booking`
4. Description: `A comprehensive local service booking platform`
5. Choose Public or Private
6. Don't initialize with README (we already have one)
7. Click "Create repository"

## Step 3: Connect Local Repository to GitHub

Copy the repository URL from GitHub (it will look like):
```
https://github.com/yourusername/local-service-booking.git
```

Add the remote repository:
```bash
git remote add origin https://github.com/yourusername/local-service-booking.git
```

## Step 4: Stage and Commit Files

Add all files to Git:
```bash
git add .
```

Commit the files:
```bash
git commit -m "Initial commit - Local Service Booking Platform"
```

## Step 5: Push to GitHub

Push to the main branch:
```bash
git push -u origin main
```

If you encounter any issues with 'main', try 'master':
```bash
git push -u origin master
```

## Step 6: Deploy to GitHub Pages (Free Static Hosting)

Since this is primarily a frontend application, you can deploy it to GitHub Pages:

### Option A: Using GitHub Pages Directly

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. Scroll down to "GitHub Pages" section
4. Under "Source", select "Deploy from a branch"
5. Choose "main" branch and "/ (root)" folder
6. Click "Save"

Your site will be available at:
```
https://yourusername.github.io/local-service-booking
```

### Option B: Using GitHub Actions for Automatic Deployment

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
```

## Step 7: Update Repository Information

1. Edit `package.json` and replace:
   - `yourusername` with your actual GitHub username
   - Update author name and email

2. Edit `README.md` and update:
   - Contact information
   - Repository URLs
   - Your name

## Step 8: Final Push

After making updates:
```bash
git add .
git commit -m "Update repository information"
git push origin main
```

## Alternative Deployment Options

### Netlify (Recommended for Full-Stack)
1. Connect your GitHub repository to [Netlify](https://netlify.com)
2. Set build command: `npm run build`
3. Set publish directory: `frontend/`
4. Get automatic deployments on every push

### Vercel (Excellent for React/Next.js)
1. Connect repository to [Vercel](https://vercel.com)
2. Automatic detection and deployment
3. Custom domain support

### Heroku (For Full-Stack with Backend)
1. Install Heroku CLI
2. Run: `heroku create your-app-name`
3. Set environment variables
4. Deploy: `git push heroku main`

## Notes

- The current setup is frontend-focused
- For full functionality, you'll need to set up the backend (MongoDB, Node.js)
- GitHub Pages only serves static files (no backend processing)
- For full booking functionality, use Netlify Functions or Vercel Serverless

## Troubleshooting

If you encounter issues:

1. **Git not recognized**: Install Git from [git-scm.com](https://git-scm.com)
2. **Permission denied**: Check your GitHub credentials
3. **Branch name issues**: Use `git branch` to see current branch name
4. **Large files**: GitHub has a 100MB file size limit

## Next Steps

After successful GitHub deployment:

1. Set up a MongoDB database (MongoDB Atlas is free)
2. Configure environment variables
3. Deploy backend to a service like Heroku, Vercel, or Netlify Functions
4. Update frontend API endpoints to point to your deployed backend
