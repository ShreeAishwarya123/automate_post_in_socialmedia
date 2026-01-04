# Complete Guide - Social Media Automation Project

## 📋 Table of Contents

1. [Setup Guide](#1-setup-guide)
2. [Step-by-Step Guide](#2-step-by-step-guide)
3. [Posting to Individual Platforms](#3-posting-to-individual-platforms)
4. [Posting to All Platforms](#4-posting-to-all-platforms)
5. [Scheduling Posts](#5-scheduling-posts)
6. [Refreshing Tokens](#6-refreshing-tokens)
7. [Postman Setup and Testing](#7-postman-setup-and-testing)

---

## 1. Setup Guide

### 1.1 Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you encounter errors, install packages one by one:
```bash
pip install pyyaml requests schedule instagrapi facebook-sdk google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 1.2 Configure Platforms

Edit `config.yaml` with your credentials:

```yaml
instagram:
  username: "your_instagram_username"
  password: "your_instagram_password"
  enabled: true

facebook:
  access_token: "your_facebook_page_access_token"
  page_id: "your_facebook_page_id"
  enabled: true

youtube:
  client_secrets_file: "client_secrets.json"
  credentials_file: "youtube_credentials.json"
  enabled: true

linkedin:
  access_token: "your_linkedin_access_token"
  person_urn: "urn:li:person:YOUR_URN"
  enabled: true

scheduler:
  check_interval: 60
  timezone: UTC
```

### 1.3 Platform-Specific Setup

#### Instagram
- Use your Instagram username and password
- First login may require manual verification
- Session will be saved automatically

#### Facebook
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app
3. Get Page Access Token with `pages_manage_posts` permission
4. Get your Page ID from Facebook Page settings

#### YouTube
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `client_secrets.json` and place in project root
6. Run authentication (browser will open)

#### LinkedIn
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create an app
3. Get token with `w_member_social` permission
4. Get your Person URN from your profile page source
5. Update `linkedin_constants.py`:
   ```python
   LINKEDIN_ACCESS_TOKEN = "your_token_here"
   LINKEDIN_PERSON_URN = "urn:li:person:YOUR_URN"
   ```

### 1.4 Test Platform Connections

```bash
# Test Instagram
python main.py test --platform instagram

# Test Facebook
python main.py test --platform facebook

# Test YouTube
python main.py test --platform youtube

# Test LinkedIn
python main.py test --platform linkedin
```

---

## 2. Step-by-Step Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Platforms
Edit `config.yaml` with your credentials (see Setup Guide above).

### Step 3: Test Connections
```bash
python main.py test --platform linkedin
```

### Step 4: Post Immediately (See Section 3)
```bash
python post_all_platforms.py "Hello from all platforms!"
```

### Step 5: Schedule Posts (See Section 5)
```bash
python main.py schedule --platform linkedin --type text --time "2024-01-15T10:00:00" --content '{"text": "Scheduled post!"}'
```

### Step 6: Run Scheduler
```bash
python main.py run
```

---

## 3. Posting to Individual Platforms

### 3.1 Post to LinkedIn

**Text Post:**
```bash
python post_linkedin.py "Hello LinkedIn!"
```

**Image Post:**
```bash
python post_linkedin.py "Check this out!" --image photo.jpg
```

### 3.2 Post to Facebook

**Text Post:**
```bash
python post_facebook.py "Hello Facebook!"
```

**Image Post:**
```bash
python post_facebook.py "Check this out!" --image photo.jpg
```

### 3.3 Post to Instagram

**Photo Post:**
```bash
python post_instagram.py "My awesome caption!" --image photo.jpg
```

**Carousel Post (2-10 images):**
```bash
python post_instagram.py "Carousel caption!" --images img1.jpg img2.jpg img3.jpg
```

### 3.4 Post to YouTube

**Basic Video Upload:**
```bash
python post_youtube.py "My Video Title" --video video.mp4
```

**Video with Description and Tags:**
```bash
python post_youtube.py "My Video Title" --video video.mp4 --description "Video description here" --tags tech tutorial programming
```

**Video with Privacy Setting:**
```bash
python post_youtube.py "My Video Title" --video video.mp4 --privacy private
```

**Privacy options:** `public`, `unlisted`, `private`

---

## 4. Posting to All Platforms

### 4.1 Post Text to All Platforms

```bash
python post_all_platforms.py "Hello from all platforms!"
```

This posts to:
- Facebook (text)
- LinkedIn (text)
- Instagram (requires image, will skip)
- YouTube (requires video, will skip)

### 4.2 Post with Image to All Platforms

```bash
python post_all_platforms.py "Check out this image!" --image photo.jpg
```

This posts to:
- Instagram (photo)
- Facebook (photo with text)
- LinkedIn (image post)

### 4.3 Post to Specific Platforms Only

```bash
python post_all_platforms.py "Hello!" --platforms facebook linkedin
```

### 4.4 Post Video to YouTube

```bash
python post_all_platforms.py "My video" --video video.mp4 --title "Video Title" --description "Video description"
```

### 4.5 Post Instagram Carousel

```bash
python post_all_platforms.py "Carousel post!" --images img1.jpg img2.jpg img3.jpg
```

### 4.6 Complete Example (Image + Video)

```bash
python post_all_platforms.py "Complete post" --image photo.jpg --video video.mp4 --title "Video Title" --platforms instagram facebook linkedin youtube
```

---

## 5. Scheduling Posts

### 5.1 Schedule a Post

**Format:** `YYYY-MM-DDTHH:MM:SS` (e.g., `2024-01-15T10:00:00`)

#### Instagram Photo
```bash
python main.py schedule --platform instagram --type photo --time "2024-01-15T10:00:00" --content '{"image_path": "photo.jpg", "caption": "My awesome post!"}'
```

#### Facebook Text Post
```bash
python main.py schedule --platform facebook --type text --time "2024-01-15T10:00:00" --content '{"message": "Hello Facebook!"}'
```

#### Facebook Photo Post
```bash
python main.py schedule --platform facebook --type photo --time "2024-01-15T10:00:00" --content '{"image_path": "photo.jpg", "message": "Check out this image!"}'
```

#### LinkedIn Text Post
```bash
python main.py schedule --platform linkedin --type text --time "2024-01-15T10:00:00" --content '{"text": "Hello LinkedIn!"}'
```

#### LinkedIn Image Post
```bash
python main.py schedule --platform linkedin --type image --time "2024-01-15T10:00:00" --content '{"text": "Check this out!", "image_path": "photo.jpg"}'
```

#### YouTube Video
```bash
python main.py schedule --platform youtube --type video --time "2024-01-15T10:00:00" --content '{"video_path": "video.mp4", "title": "My Video", "description": "Video description", "tags": ["tag1", "tag2"], "privacy_status": "public"}'
```

#### Instagram Carousel
```bash
python main.py schedule --platform instagram --type carousel --time "2024-01-15T10:00:00" --content '{"image_paths": ["img1.jpg", "img2.jpg", "img3.jpg"], "caption": "Carousel post!"}'
```

### 5.2 List Scheduled Posts

```bash
# List all posts
python main.py list

# List only scheduled posts
python main.py list --status scheduled

# List only posted posts
python main.py list --status posted

# List failed posts
python main.py list --status failed
```

### 5.3 Run the Scheduler

Start the scheduler to automatically post scheduled content:

```bash
python main.py run
```

The scheduler will:
- Check for scheduled posts every 60 seconds
- Execute posts when their scheduled time arrives
- Save post status and results

**Keep the scheduler running** - it will post automatically at scheduled times.

---

## 6. Refreshing Tokens

### 6.1 Refresh LinkedIn Token

1. Go to: https://www.linkedin.com/developers/tools/access-token
2. Select your app
3. Select `w_member_social` scope
4. Generate new token
5. Update `linkedin_constants.py`:
   ```python
   LINKEDIN_ACCESS_TOKEN = "YOUR_NEW_TOKEN"
   ```
6. Sync to config.yaml:
   ```bash
   python sync_linkedin_config.py
   ```

### 6.2 Refresh Facebook Token

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app
3. Add `pages_manage_posts` permission
4. Generate token for your page
5. Update `config.yaml`:
   ```yaml
   facebook:
     access_token: "YOUR_NEW_TOKEN"
   ```

### 6.3 Refresh YouTube Token

YouTube tokens refresh automatically. If you need to re-authenticate:

1. Delete `youtube_credentials.json`
2. Run any YouTube command - browser will open for authentication

### 6.4 Refresh Instagram Session

Instagram sessions are saved automatically. If login fails:

1. Delete `instagram_session_*.json` file
2. Run Instagram post - it will prompt for login again

---

## 7. Postman Setup and Testing

### 7.1 Import Postman Collection

1. Open Postman
2. Click **"Import"** (top left)
3. Select file: `linkedin_postman_collection.json`
4. Collection will be imported with your credentials

### 7.2 Test LinkedIn Post in Postman

1. Open **"Post Text"** request in the collection
2. Click **"Send"**
3. Check response:
   - **201 Created**: Success! Post created
   - **403 Forbidden**: Token issue - refresh token
   - **422 Unprocessable**: URN format issue

### 7.3 Update Postman Collection

If you update your LinkedIn token/URN:

```bash
python update_postman_collection.py
```

This updates `linkedin_postman_collection.json` with current values.

### 7.4 Manual Postman Setup

**Method:** `POST`  
**URL:** `https://api.linkedin.com/v2/ugcPosts`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
X-Restli-Protocol-Version: 2.0.0
```

**Body (raw JSON):**
```json
{
  "author": "urn:li:person:YOUR_URN",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Test post from Postman!"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

**Expected Response (201):**
```json
{
  "id": "urn:li:share:7413587367162204160"
}
```

---

## 📋 Quick Reference Commands

### Test Platforms
```bash
python main.py test --platform instagram
python main.py test --platform facebook
python main.py test --platform youtube
python main.py test --platform linkedin
```

### Post to Individual Platforms
```bash
# LinkedIn
python post_linkedin.py "Hello LinkedIn!"
python post_linkedin.py "Check this!" --image photo.jpg

# Facebook
python post_facebook.py "Hello Facebook!"
python post_facebook.py "Check this!" --image photo.jpg

# Instagram
python post_instagram.py "My caption!" --image photo.jpg
python post_instagram.py "Carousel!" --images img1.jpg img2.jpg img3.jpg

# YouTube
python post_youtube.py "Video Title" --video video.mp4
python post_youtube.py "Video Title" --video video.mp4 --description "Description" --tags tech tutorial
```

### Post to All Platforms
```bash
# All platforms
python post_all_platforms.py "Hello!"

# With image
python post_all_platforms.py "Check this!" --image photo.jpg

# Specific platforms
python post_all_platforms.py "Hello!" --platforms facebook linkedin
```

### Schedule Posts
```bash
python main.py schedule --platform linkedin --type text --time "2024-01-15T10:00:00" --content '{"text": "Hello!"}'
```

### List Scheduled Posts
```bash
python main.py list
```

### Run Scheduler
```bash
python main.py run
```

### Update LinkedIn Token
1. Edit `linkedin_constants.py`
2. Run: `python sync_linkedin_config.py`

### Update Postman Collection
```bash
python update_postman_collection.py
```

---

## ⚠️ Important Notes

### Time Format
- Use ISO format: `YYYY-MM-DDTHH:MM:SS`
- Example: `2024-01-15T10:00:00`
- Times are in local timezone (or UTC if specified)

### File Paths
- Use absolute paths or paths relative to where you run the command
- Example: `C:\Users\YourName\Desktop\photo.jpg` or `photo.jpg` (if in same directory)

### Platform Requirements
- **Instagram**: Requires image (photo or carousel)
- **Facebook**: Text or image
- **LinkedIn**: Text or image
- **YouTube**: Requires video

### Token Management
- **LinkedIn**: Update in `linkedin_constants.py` (one place)
- **Facebook**: Update in `config.yaml`
- **YouTube**: Auto-refreshes
- **Instagram**: Session saved automatically

### Scheduler
- Keep `python main.py run` running for scheduled posts
- Checks every 60 seconds
- Posts execute when scheduled time arrives

---

## 🆘 Troubleshooting

### "Platform not initialized"
- Check `config.yaml` - platform must be `enabled: true`
- Verify credentials are correct
- Run test: `python main.py test --platform PLATFORM_NAME`

### "Token expired"
- Refresh token (see Section 6)
- Update in `config.yaml` or `linkedin_constants.py`

### "File not found"
- Use absolute paths
- Check file exists
- Verify file path is correct

### "Scheduled post not posting"
- Make sure scheduler is running: `python main.py run`
- Check scheduled time is in the future
- Verify post status: `python main.py list`

---

## 📁 Project Structure

```
.
├── main.py                      # Main scheduler CLI
├── scheduler.py                 # Scheduler engine
├── post_all_platforms.py        # Post to all platforms
├── post_linkedin.py             # Post to LinkedIn only
├── linkedin_constants.py        # LinkedIn credentials (update here)
├── sync_linkedin_config.py      # Sync LinkedIn constants to config
├── update_postman_collection.py # Update Postman collection
├── config.yaml                  # Platform configuration
├── linkedin_postman_collection.json  # Postman collection
├── requirements.txt             # Python dependencies
├── platforms/                   # Platform modules
│   ├── instagram.py
│   ├── facebook.py
│   ├── youtube.py
│   └── linkedin.py
├── scheduled_posts.json         # Scheduled posts (auto-generated)
└── COMPLETE_GUIDE.md           # This guide
```

---

## ✅ Checklist for New Users

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure `config.yaml` with all platform credentials
- [ ] Configure `linkedin_constants.py` with LinkedIn token/URN
- [ ] Create sample media: `python create_sample_media.py`
- [ ] Test each platform: `python main.py test --platform PLATFORM`
- [ ] Test posting: `python post_all_platforms.py "Test post" --image sample_image.jpg`
- [ ] Test scheduling: Schedule a post and run scheduler
- [ ] Import Postman collection and test

---

## 📸 Sample Media Files

### Create Sample Image and Video

```bash
python create_sample_media.py
```

This creates:
- `sample_image.jpg` - Ready to use for testing (1080x1080)
- Instructions for creating sample video

### Test with Sample Image

```bash
# Test LinkedIn
python post_linkedin.py "Test with sample image!" --image sample_image.jpg

# Test Facebook
python post_facebook.py "Test!" --image sample_image.jpg

# Test Instagram
python post_instagram.py "Test caption!" --image sample_image.jpg

# Test All Platforms
python post_all_platforms.py "Testing all!" --image sample_image.jpg
```

**You're all set! Start posting to all platforms!** 🚀

