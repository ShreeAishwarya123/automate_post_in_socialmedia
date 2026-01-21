# 🚀 Quick Start - Social Media Automation Platform

## ⚡ 5-Minute Setup

### You Received This Folder?
This `docker/` folder contains everything needed to deploy the Social Media Automation Platform.

### Step 1: Install Docker
Make sure you have Docker installed:
- **Windows/Mac**: Download from https://docker.com
- **Linux**: `sudo apt install docker.io docker-compose`

### Step 2: Configure Google Access
```bash
# Copy the environment template
cp .env.example .env

# Edit .env file - you NEED these:
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**How to get Google credentials:**
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable "Gemini AI API" and "Google Drive API"
4. Create "OAuth 2.0 Client ID" credentials
5. Copy Client ID and Client Secret to .env

### Step 3: Deploy
```bash
# Start everything (first time takes ~5 minutes)
docker-compose up -d

# OR use the easy script
./deploy.sh --dev
```

### Step 4: Access Your App
Open your browser:
- **Main App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### Step 5: Add Social Media Accounts
1. Go to http://localhost:3000
2. Create an account
3. Connect your social media accounts (Instagram, Facebook, etc.)
4. Start creating posts!

## 🛠️ Management Commands

```bash
# Check if everything is running
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop everything
docker-compose down

# Restart
docker-compose restart

# Complete cleanup (removes all data!)
docker-compose down -v
```

## ❓ Having Issues?

**Can't access the app?**
- Wait 2-3 minutes after `docker-compose up -d`
- Check if ports 3000/8000 are available
- Run `docker-compose logs` to see errors

**Google login not working?**
- Double-check your Client ID and Secret in `.env`
- Make sure your Google Cloud project has the APIs enabled

**Out of memory?**
- Increase Docker memory to 4GB+ in Docker settings
- Close other applications

**Need help?** Check the main README.md file in this folder for detailed troubleshooting.

---

**🎉 That's it! Your AI-powered social media automation is ready.**