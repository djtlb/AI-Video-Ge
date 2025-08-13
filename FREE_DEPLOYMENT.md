# AI Avatar Video - Free Deployment Guide

This guide provides instructions for deploying the AI Avatar Video application on various free hosting platforms.

## Option 1: Deploy on Render.com (Free Tier)

Render offers a reliable free tier perfect for this application.

### Render Deployment Steps

1. Create a Render account at [render.com](https://render.com)
2. Run the deployment script:

   ```bash
   ./deploy_to_render.sh
   ```

3. Once deployed, your application will be available at a URL like: `https://ai-avatar-video.onrender.com`

**Free Tier Limitations:**

- Spins down after 15 minutes of inactivity
- 512 MB RAM
- 0.1 CPU
- Limited bandwidth
- 1GB persistent disk

## Option 2: Deploy on Netlify (Free Tier)

Netlify is excellent for static sites with serverless functions.

### Netlify Deployment Steps

1. Create a Netlify account at [netlify.com](https://netlify.com)
2. Run the deployment script:

   ```bash
   ./deploy_to_netlify.sh
   ```

3. Once deployed, your application will be available at your Netlify domain

**Free Tier Limitations:**

- 100GB bandwidth/month
- 300 minutes build time/month
- Limited serverless function execution

## Option 3: Deploy on Railway App (Free Tier)

Railway provides a user-friendly platform with a generous free tier.

### Railway Deployment Steps

1. Create a Railway account at [railway.app](https://railway.app)
2. Run the deployment script:

   ```bash
   ./deploy_to_railway.sh
   ```

3. Once deployed, your application will be available at your Railway domain

**Free Tier Limitations:**

- $5 credit/month
- 512 MB RAM
- 1 GB disk
- Credit expires after 21 days for new users

## Option 4: Run on Replit (Free Tier)

Replit is a browser-based IDE with hosting capabilities.

### Replit Setup Steps

1. Create a Replit account at [replit.com](https://replit.com)
2. Create a new Python repl
3. Import your GitHub repository or upload your files
4. Add a `.replit` file with the following content:

   ```toml
   run = "python -m uvicorn app.main:app --host 0.0.0.0 --port 8080"
   ```

5. Click "Run"

**Free Tier Limitations:**

- Limited compute resources
- Public code by default
- Sleeps after inactivity

## Option 5: Run on GitHub Codespaces with Port Forwarding

GitHub Codespaces provides a development environment and can be used for demos.

### GitHub Codespaces Setup Steps

1. Push your code to a GitHub repository
2. Click "Code" and select "Open with Codespaces"
3. In the terminal, run:

   ```bash
   ./run_standalone.sh
   ```

4. Use port forwarding to access your application

**Free Tier Limitations:**

- 60 hours/month of usage
- 15GB of storage
- Not meant for production deployment

## Important Notes for All Free Deployments

1. **Storage Limitations**: Free tiers have limited storage. Consider using external storage services for production.
2. **Performance**: Free tiers often have limited CPU and RAM.
3. **Inactivity Timeouts**: Most free services shut down after periods of inactivity.
4. **Database Persistence**: Ensure your SQLite database is in a persistent storage location.

## Local Deployment

For the most reliable experience, consider running the application locally:

```bash
./run_standalone.sh
```

This will run the application on your local machine without any cloud service limitations.
