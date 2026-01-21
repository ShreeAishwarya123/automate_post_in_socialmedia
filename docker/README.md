# 🐳 Docker Deployment for Social Media Automation Platform

**Share this entire `docker/` folder with anyone to enable them to deploy the Social Media Automation Platform.**

## 📦 What's Included

This folder contains everything needed to deploy the platform via Docker:

```
docker/
├── docker-compose.yml          # Main orchestration file
├── docker-compose.override.yml # Development overrides
├── Dockerfile                  # Backend container build
├── Dockerfile.frontend         # Frontend container build
├── nginx.conf                  # Production web server config
├── .env.example               # Environment template
├── .dockerignore              # Build optimization
├── deploy.sh                  # Interactive deployment script
└── README.md                  # This file
```

## 🚀 Quick Deployment (3 Steps)

### Prerequisites for Recipient
- **Docker Engine** 20.10+ installed
- **Docker Compose** 2.0+ installed
- **4GB+ RAM** available
- **Google Account** with Gemini access

### Step 1: Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
# REQUIRED: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
# OPTIONAL: Social media platform credentials
```

### Step 2: Deploy
```bash
# Quick development deployment
docker-compose up -d

# OR use interactive script
chmod +x deploy.sh  # Linux/Mac
./deploy.sh         # Interactive menu

# OR quick commands
./deploy.sh --dev   # Development mode
./deploy.sh --prod  # Production mode
```

### Step 3: Access Application
```
🌐 Web UI:     http://localhost:3000  (Development)
📚 API Docs:   http://localhost:8000/docs
🔒 Production: https://localhost     (with SSL)
```

## 🔑 Required Setup

### Google Services (MANDATORY)
You need a Google Cloud Console project with:
1. **Gemini AI API** enabled
2. **Google Drive API** enabled
3. **OAuth 2.0 credentials** created

Get credentials from: https://console.cloud.google.com/

### Environment Variables
Edit `.env` file with:
```bash
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
SECRET_KEY=your-random-secret-key-here
```

## 📋 Deployment Modes

### Development Mode (Recommended)
- Hot reload enabled
- Debug logging
- Local ports exposed
- No SSL required

### Production Mode
- SSL/HTTPS enabled
- Nginx reverse proxy
- Optimized for performance
- Requires SSL certificates

## 🐛 Troubleshooting

### Common Issues
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart

# Complete cleanup
docker-compose down -v
docker system prune -f
```

### Memory Issues
If containers fail to start:
```bash
# Increase Docker memory in Docker Desktop
# Settings → Resources → Memory (set to 4GB+)
```

### Permission Issues
```bash
# Fix volume permissions (Linux/Mac)
sudo chown -R 1000:1000 gemini_automation/
sudo chown -R 1000:1000 downloaded_content/
```

## 🔄 Updates

To update the platform:
```bash
# Pull latest source code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 📊 Architecture

```
┌─────────────────┐
│   React UI      │ ← Port 3000
│   (Frontend)    │
└─────────────────┘
         │
    ┌────────────┐
    │   FastAPI   │ ← Port 8000
    │  (Backend)  │
    └────────────┘
         │
    ┌────────────┐
    │ Gemini AI   │
    │ Social APIs │
    └────────────┘
```

## 🛡️ Security Notes

- **Change default secrets** in production
- **Use strong passwords** for database
- **Regular backups** of persistent volumes
- **Monitor access logs** for suspicious activity

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify environment variables in `.env`
3. Ensure Google credentials are correct
4. Check system resources (RAM, disk space)

**The entire source code repository is required** - these Docker files only provide the deployment infrastructure.