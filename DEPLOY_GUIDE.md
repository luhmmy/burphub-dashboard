# Deploy BurpHub Dashboard to Render

## ✅ GitHub Setup Complete
**Repository**: https://github.com/luhmmy/burphub-dashboard

---

## Next: Deploy to Render

### Step 1: Sign in to Render
1. Go to **https://render.com**
2. Sign in with your GitHub account

### Step 2: Create New Blueprint
1. Click **New** → **Blueprint**
2. Connect to GitHub if prompted
3. Select repository: **luhmmy/burphub-dashboard**
4. Render will detect `render.yaml` automatically

### Step 3: Review and Deploy
Render will show:
- ✅ **PostgreSQL Database**: `burphub-db`
- ✅ **Web Service**: `burphub-dashboard`

Click **Apply** to start deployment!

### Step 4: Wait for Deployment (3-5 minutes)
You'll see:
```
Creating database...
Installing dependencies...
Starting web service...
```

### Step 5: Get Your Credentials

Once deployed:

#### A. Dashboard URL
- Go to your `burphub-dashboard` service
- Copy the URL: `https://burphub-dashboard-XXXX.onrender.com`

#### B. API Key
- Click **Environment** tab
- Find `SYNC_API_KEY`
- Copy the value (it's auto-generated)

---

## Configure Burp Suite

Create a file: `C:\burp-cloud-sync.bat`

```batch
@echo off
java -Dburphub.api.url=https://YOUR-URL-HERE.onrender.com/api/sync ^
     -Dburphub.api.key=YOUR_API_KEY_HERE ^
     -jar "C:\Program Files\BurpSuitePro\burpsuite_pro.jar"
```

**Replace:**
- `YOUR-URL-HERE` with your Render dashboard URL
- `YOUR_API_KEY_HERE` with the `SYNC_API_KEY` from Render

---

## Test It!

1. Run `burp-cloud-sync.bat` to launch Burp Suite
2. Load the updated `BurpHub.jar` extension
3. Use Burp Suite normally
4. Close Burp → Check console for "Cloud sync successful!"
5. Visit your dashboard URL → See your activity! 🔥

---

## Share with Interviewers

Just send them your Render URL:
```
https://your-dashboard.onrender.com
```

No login needed - it's a public showcase of your red team skills!
