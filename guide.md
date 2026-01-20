# Gemini AI Instagram Posting Guide

This guide explains how to use the integrated Gemini-Hive system to generate content with Google Gemini AI and automatically post it to Instagram.

## System Overview

The integration combines two main components:

1. **Gemini Automation**: Browser automation scripts that interact with Google Gemini AI to generate images, videos, and presentations
2. **Hive Platform**: FastAPI-based social media management system that handles posting to multiple platforms

## Features

- ✅ Generate images using Gemini AI prompts
- ✅ Generate videos using Gemini AI prompts
- ✅ Generate presentations (PPT) using Gemini AI
- ✅ Automatic upload to Google Drive
- ✅ One-click posting to Instagram
- ✅ Database tracking of all posts and status
- ✅ REST API for integration

## API Usage

### 1. Authentication

First, create a user account and get an access token:

```bash
# Register user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "full_name": "Your Name",
    "password": "yourpassword"
  }'

# Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=yourpassword"
```

### 2. Configure Instagram Credentials

```bash
# Add Instagram credentials
curl -X POST "http://localhost:8000/api/credentials" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "credential_type": "username_password",
    "credential_data": {
      "username": "your_instagram_username",
      "password": "your_instagram_password"
    }
  }'
```

### 3. Generate and Post Content

#### Generate an Image

```bash
curl -X POST "http://localhost:8000/api/posts/generate-and-post" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "prompt=A beautiful sunset over mountains with vibrant colors and dramatic lighting" \
  -F "content_type=IMAGE" \
  -F "platforms=[\"instagram\"]" \
  -F "caption=AI-generated sunset using Gemini AI! #AIArt #GeneratedArt"
```

#### Generate a Video

```bash
curl -X POST "http://localhost:8000/api/posts/generate-and-post" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "prompt=A short animation of a rocket launching into space with stars and galaxies" \
  -F "content_type=VIDEO" \
  -F "platforms=[\"instagram\"]" \
  -F "caption=AI-generated rocket animation using Gemini AI! #AIAnimation #Space"
```

#### Generate a Presentation

```bash
curl -X POST "http://localhost:8000/api/posts/generate-and-post" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "prompt=Create a presentation about renewable energy solutions" \
  -F "content_type=PPT" \
  -F "platforms=[\"instagram\"]" \
  -F "caption=AI-generated presentation on renewable energy #AIPresentation"
```

## API Response

Successful requests return:

```json
{
  "post_id": 123,
  "gemini_prompt": "A beautiful sunset over mountains...",
  "content_type": "IMAGE",
  "generated_content": "https://drive.google.com/file/d/abc123...",
  "caption": "AI-generated sunset using Gemini AI! #AIArt",
  "platforms": ["instagram"],
  "results": [
    {
      "platform": "instagram",
      "status": "posted",
      "post_url": "https://instagram.com/p/ABC123/",
      "post_id": "instagram_123"
    }
  ]
}
```

## Setup Requirements

### 1. Google Drive API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create credentials (OAuth 2.0 Client ID)
5. Download `credentials.json` and place it in `gemini_automation/gemini_automation/auth/`

### 2. Browser User Data

The system uses Playwright for browser automation. The user data directory should contain:

- `gemini_automation/gemini_automation/auth/user_data/` - Browser profile with Gemini AI access
- Pre-configured Chrome profile with Gemini AI logged in

### 3. Social Media Credentials

Configure credentials through the API for each platform you want to post to.

## File Structure

```
hive/
├── app/
│   ├── routers/
│   │   └── posts.py          # Main API endpoint with Gemini integration
│   ├── models.py             # Database models
│   └── main.py               # FastAPI application
├── flows/
│   ├── gemini_flow.py        # Gemini AI interaction logic
│   └── drive_flow.py         # Google Drive upload logic
├── platforms/
│   └── instagram.py          # Instagram posting automation
└── gemini_automation/
    └── gemini_automation/
        ├── auth/
        │   ├── credentials.json       # Google Drive API credentials
        │   └── user_data/             # Browser profile for Gemini access
        ├── flows/                     # Flow scripts (imported from root flows/)
        ├── prompts.xlsx              # Excel file with content prompts
        └── runner.py                  # Main automation runner
```

## Supported Content Types

- **IMAGE**: Generates images using Gemini AI
- **VIDEO**: Generates videos/animations using Gemini AI
- **PPT**: Generates presentations using Gemini AI

## Supported Platforms

Currently implemented:
- **Instagram**: Images and videos (Reels)

Extensible to other platforms by adding new platform modules.

## Error Handling

The API provides detailed error messages for:
- Invalid authentication
- Missing credentials
- Gemini AI generation failures
- Platform posting failures
- File upload issues

## Testing

Run the integration tests:

```bash
# Basic integration test
python test_gemini_integration.py

# Demo of API usage
python demo_gemini_instagram_post.py
```

## Troubleshooting

### Common Issues

1. **"Gemini AI service not available"**
   - Check that `flows/gemini_flow.py` can be imported
   - Verify browser user data is configured correctly

2. **"Google Drive credentials not configured"**
   - Ensure `credentials.json` exists in the auth directory
   - Check file permissions

3. **"Instagram login failed"**
   - Verify Instagram credentials are correct
   - Check if Instagram requires additional verification

4. **"Platform not implemented"**
   - Only Instagram is currently implemented for Gemini posts
   - Other platforms need additional platform modules

### Debug Mode

Enable debug logging by checking the server console output when making API calls.

## Security Notes

- Credentials are encrypted in the database
- Google Drive credentials should be kept secure
- Instagram passwords are stored encrypted
- Use HTTPS in production
- Implement rate limiting for API calls

## Future Enhancements

- Support for additional social media platforms
- Batch processing of multiple prompts
- Scheduled posting with Gemini generation
- Content editing and enhancement features
- Analytics and performance tracking</content>
</xai:function_call">Created file GEMINI_INSTAGRAM_GUIDE.md with comprehensive documentation for the integrated system.