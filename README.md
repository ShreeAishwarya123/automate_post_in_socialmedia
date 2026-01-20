# 🤖 Social Media Automation Platform

**Multi-user web platform** for automated social media posting with AI content generation. Users can connect their own social media accounts and schedule posts across Instagram, Facebook, YouTube, and LinkedIn.

## ✨ Features

- 🎨 **AI Content Generation**: Create images, videos, and presentations with Google Gemini
- 📱 **Multi-Platform Posting**: Instagram, Facebook, YouTube, LinkedIn
- 🔄 **Automated Workflow**: Generate → Store → Post in one command
- 📊 **Excel Management**: Track prompts, captions, and posting status
- ☁️ **Cloud Storage**: Automatic Google Drive integration
- 🎯 **Separate Prompts**: Technical prompts for AI, custom captions for social media

## 🚀 Quick Start (3 minutes)

```bash
# 1. Clone or download the project
# 2. Run the interactive setup wizard
python setup.py

# 3. Follow the prompts to connect your accounts:
#    - Google Gemini & Drive (required)
#    - Instagram, Facebook, YouTube, LinkedIn (optional)

# 4. Edit the Excel file with your content
# Location: gemini_automation/gemini_automation/prompts.xlsx

# 5. Generate and post content
python generatepost.py --platforms youtube instagram
```

**That's it!** 🎉 Your AI-powered social media automation is ready.

## 📋 Prerequisites

- Python 3.8+
- Google account with Gemini access
- Social media accounts (optional, setup wizard will guide you)

## 🎯 Usage

### Step 1: Initial Setup (One-time)
```bash
python setup.py
```
Interactive wizard guides you through connecting all your accounts.

### Step 2: Add Content to Excel
Edit `gemini_automation/gemini_automation/prompts.xlsx`:

| Prompt | Type | Caption | Status |
|--------|------|---------|--------|
| "A beautiful sunset over mountains" | VIDEO | "Check out this amazing AI-generated sunset! 🌅 #Nature #AI" | Pending |

### Step 3: Generate & Post
```bash
# Generate content and post to platforms
python generatepost.py --platforms youtube instagram facebook

# Options
python generatepost.py --help
```

### Available Commands
- `python setup.py` - Interactive account setup wizard
- `python generatepost.py` - Generate content and post
- `python generatepost.py --dry-run` - Preview without posting

### Separate Workflows (Legacy)

#### Generate Content (Gemini Automation)
```bash
# In gemini_automation/gemini_automation/
python runner.py
```
This processes `prompts.xlsx` and generates content based on Type (IMAGE/VIDEO/PPT).

### Post Generated Content (Integrated)
```bash
# Post all completed tasks to all platforms
python post_from_drive.py

# Post only images to Facebook and LinkedIn
python post_from_drive.py --type image --platforms facebook linkedin

# Post specific content by prompt text
python post_from_drive.py --prompt "sunset over mountains"

# Dry run to see what would be posted
python post_from_drive.py --dry-run
```

## Content Types Supported

- **IMAGE**: Downloads PNG files and posts as images
- **VIDEO**: Downloads MP4 files and posts to YouTube
  - When YouTube is selected as a platform, Gemini automatically generates:
    - **Title**: Catchy YouTube title (max 100 chars)
    - **Description**: Engaging description (max 5000 chars)
    - **Tags**: 5-10 relevant tags
- **PPT**: Downloads as PDF, posts link in text (PDFs not directly supported by platforms)

## 📊 Excel Content Management

Your content is managed in: `gemini_automation/gemini_automation/prompts.xlsx`

### Column Structure

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| **Prompt** | Technical prompt for Gemini AI | Yes | "A cinematic drone shot of a forest" |
| **Type** | Content type: IMAGE, VIDEO, PPT | Yes | "VIDEO" |
| **Caption** | Social media post text | Yes | "🌲 Explore nature's beauty! #NatureVibes" |
| **Status** | Auto-managed: Pending → Running → Completed | Auto | "Pending" |
| **Drive_Link** | Auto-generated Google Drive link | Auto | Auto-filled |
| **Posted_Status** | Posting results | Auto | "Posted to instagram, facebook" |

### How It Works
- **Prompt** → Sent to Gemini for content generation
- **Caption** → Used as the social media post text
- **Type** → Determines generation method (image/video/PPT)
- Status tracking prevents duplicate processing

### Adding Content
1. Open the Excel file
2. Add rows with your prompts and captions
3. Set Status to "Pending"
4. Save and run `python generatepost.py`

**Important**: The **Prompt** column is used for AI content generation, while the **Caption** column is used for social media posting text.

## Workflow Example

### Unified Workflow (Recommended)
1. **Prepare Excel**:
   - Edit `gemini_automation/gemini_automation/prompts.xlsx`
   - Add row with: Prompt (for AI generation), Type (IMAGE/VIDEO/PPT), Caption (posting text), Status='Pending'

2. **One Command - Generate + Post**:
   ```bash
   python generatepost.py --platforms instagram facebook linkedin
   ```
   - Uses **Prompt** column for Gemini content generation
   - Uses **Caption** column for social media posting text
   - Automatically generates content, uploads to Drive, posts to platforms
   - Updates Excel with completion status

### Separate Workflow (Legacy)
1. **Prepare Prompts**: Same as above

2. **Generate Content**:
   ```bash
   cd gemini_automation/gemini_automation
   python runner.py
   ```
   - Status changes to 'Completed' with Drive links

3. **Post to Social Media**:
   ```bash
   cd ../..  # Back to hive root
   python post_from_drive.py --platforms instagram facebook linkedin
   ```

## Troubleshooting

### Drive Download Issues
- Ensure Gemini automation completed successfully
- Check network connectivity for large files
- Verify Google Drive permissions

### Platform Posting Issues
- Check `config.yaml` credentials
- Verify platform API permissions
- For Instagram: May require manual session refresh
- For Facebook: Ensure Page Access Token is valid

### PPT/Content Issues
- PPT files are converted to PDF
- Social platforms don't support PDF posting directly
- Content is posted as text with link

## File Structure After Integration

```
hive/
├── gemini_automation/           # Gemini content generation
├── downloaded_content/          # Cached downloads from Drive
├── gemini_reader.py            # Excel reader
├── drive_downloader.py         # Drive download utility
├── post_from_drive.py          # Main integration script
├── platforms/                  # Posting platforms
├── config.yaml                # Platform configurations
└── requirements.txt           # Updated dependencies
```

## 🔄 Multi-User API System (New!)

This project now includes a **complete web API** for multi-user access with a React frontend. Perfect for:

- **Multiple Users**: Each user can connect their own social media accounts
- **Web Interface**: Beautiful React UI instead of command line
- **Secure API**: JWT authentication with encrypted credential storage
- **RESTful Endpoints**: Well-documented API for integrations

### 🚀 API Quick Start

```bash
# Install additional dependencies
pip install -r requirements.txt

# Start both backend and frontend
python start.py

# Access the web application
# 🌐 Web App: http://localhost:3000
# 📚 API Docs: http://localhost:8000/docs
```

### 🏗️ API Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI        │    │   Database      │
│   (Frontend)    │◄──►│   (Backend)      │◄──►│   (SQLite)      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • User Auth     │    │ • Users         │
│ • Post Creator  │    │ • Credentials   │    │ • Credentials   │
│ • Account Mgmt  │    │ • Posts API     │    │ • Posts         │
│ • Scheduling    │    │ • Platform APIs │    │ • Platforms     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                   ┌─────────────────┐
                   │ Social Platforms │
                   │ • Instagram     │
                   │ • Facebook      │
                   │ • YouTube       │
                   │ • LinkedIn      │
                   └─────────────────┘
```

### 📡 API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

#### Credentials Management
- `GET /api/credentials` - List user credentials
- `POST /api/credentials` - Add new credential
- `PUT /api/credentials/{id}` - Update credential
- `DELETE /api/credentials/{id}` - Delete credential

#### Posts Management
- `GET /api/posts` - List user posts
- `POST /api/posts` - Create new post
- `POST /api/posts/{id}/publish` - Publish post to platforms
- `DELETE /api/posts/{id}` - Delete post

#### Platform Operations
- `GET /api/platforms/supported` - List supported platforms
- `POST /api/platforms/test-credential/{id}` - Test credential validity

### 🔒 Security Features

- **Password Hashing**: bcrypt for secure password storage
- **JWT Authentication**: Token-based authentication
- **Credential Encryption**: API keys stored securely
- **CORS Protection**: Configured for frontend access
- **Input Validation**: Pydantic models for data validation

### 🗂️ API Project Structure

```
social-media-automation/
├── app/                    # FastAPI backend
│   ├── main.py            # Main FastAPI app
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection
│   ├── models.py          # SQLAlchemy models
│   ├── auth.py            # Authentication utilities
│   └── routers/           # API route handlers
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   └── App.js         # Main React app
│   └── package.json
├── platforms/             # Social media platform handlers
├── gemini_automation/     # Gemini AI integration
├── start.py              # Startup script
└── README.md
```

## Future Enhancements

- Add posting status tracking back to Excel
- Support for more content types
- PDF to image conversion for better posting
- Automated scheduling integration
- Advanced analytics dashboard
- Bulk post creation
- Social media insights integration
- Custom workflow automation