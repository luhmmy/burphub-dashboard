# BurpHub Cloud Dashboard

Share your BurpHub activity with interviewers via a beautiful, public URL.

## Features

- 🔥 **Red Teamer Theme** - Crimson red and Burp Suite orange color scheme
- 📊 **GitHub-Style Heatmap** - 365-day contribution graph
- 🎯 **Live Stats** - Current streak, total requests, active days
- 🛠️ **Tool Breakdown** - Proxy, Repeater, Intruder, Scanner usage
- 🌐 **Cloud Synced** - PostgreSQL on Render for persistence

## Deploy to Render

### 1. Push to GitHub

```bash
cd dashboard
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. Create Render Services

1. Go to [render.com](https://render.com)
2. Click **New** → **Blueprint**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml` and create:
   - PostgreSQL database
   - Web service

### 3. Get Your URLs

After deployment:
- **Dashboard URL**: `https://burphub-dashboard.onrender.com`
- **Sync API**: `https://burphub-dashboard.onrender.com/api/sync`

### 4. Get Your API Key

1. Go to your Render dashboard
2. Click on **bur phub-dashboard** service
3. Go to **Environment** tab
4. Copy the `SYNC_API_KEY` value

## Configure BurpHub Extension

You'll need to modify the BurpHub Java extension to sync to your Render URL.

Add to `BurpHub.java` (we'll do this in the next step):

```java
// Sync to cloud on session end
CloudSync.syncData("https://burphub-dashboard.onrender.com/api/sync", 
                   "YOUR_API_KEY_HERE", 
                   database);
```

## Local Testing

```bash
cd dashboard

# Install dependencies
pip install -r requirements.txt

# Set environment
export DATABASE_URL=sqlite:///test.db
export SYNC_API_KEY=dev-key

# Run
python app.py
```

Visit: http://localhost:5000

## Share with Interviewers

Simply send them your Render URL:
```
https://burphub-dashboard.onrender.com
```

No login required - it's a public showcase of your Burp Suite activity!
