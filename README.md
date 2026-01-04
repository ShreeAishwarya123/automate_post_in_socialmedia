# Social Media Automation & Scheduling

A Python-based automation tool for scheduling and posting content to Instagram, Facebook, YouTube, and LinkedIn. This tool allows you to schedule posts across multiple platforms without using n8n.

## Features

- ✅ **Instagram**: Post photos and carousels with captions
- ✅ **Facebook**: Post text and images to Facebook Pages
- ✅ **YouTube**: Upload and schedule videos
- ✅ **LinkedIn**: Post text and images
- ✅ **Unified Scheduler**: Schedule posts across all platforms
- ✅ **No n8n Required**: Pure Python implementation

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure platforms** in `config.yaml`

3. **See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) for full instructions**

## Quick Commands

**Post to all platforms:**
```bash
python post_all_platforms.py "Hello from all platforms!"
```

**Schedule a post:**
```bash
python main.py schedule --platform linkedin --type text --time "2024-01-15T10:00:00" --content '{"text": "Hello!"}'
```

**Run scheduler:**
```bash
python main.py run
```

**For complete guide, see [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)**

## Platform Setup

### Instagram

1. Use your Instagram username and password
2. The tool will handle 2FA challenges (you may need to verify manually on first login)
3. Session will be saved for future use

**config.yaml**:
```yaml
instagram:
  username: "your_username"
  password: "your_password"
  enabled: true
```

### Facebook

1. Create a Facebook App at [Facebook Developers](https://developers.facebook.com/)
2. Get a Page Access Token with `pages_manage_posts` permission
3. Get your Page ID from your Facebook Page settings

**config.yaml**:
```yaml
facebook:
  access_token: "your_page_access_token"
  page_id: "your_page_id"
  enabled: true
```

**How to get Facebook Page Access Token**:
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Add `pages_manage_posts` permission
4. Generate token for your page
5. Use the generated token

### YouTube

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `client_secrets.json` and place it in the project root
6. Run authentication once - it will open a browser for authorization

**config.yaml**:
```yaml
youtube:
  client_secrets_file: "client_secrets.json"
  credentials_file: "youtube_credentials.json"
  enabled: true
```

### LinkedIn

1. Create a LinkedIn App at [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Request access to Marketing Developer Platform
3. Generate an access token with `w_member_social` permission
4. Get your Person URN (format: `urn:li:person:xxxxx`)

**config.yaml**:
```yaml
linkedin:
  access_token: "your_access_token"
  person_urn: "urn:li:person:xxxxx"
  enabled: true
```

## Usage

### Test Platform Connection

```bash
python main.py test --platform instagram
python main.py test --platform facebook
python main.py test --platform youtube
python main.py test --platform linkedin
```

### Schedule a Post

**Instagram Photo**:
```bash
python main.py schedule --platform instagram --type photo --time "2024-01-15T10:00:00" --content '{"image_path": "path/to/image.jpg", "caption": "My awesome post!"}'
```

**Facebook Text Post**:
```bash
python main.py schedule --platform facebook --type text --time "2024-01-15T10:00:00" --content '{"message": "Hello Facebook!"}'
```

**Facebook Photo Post**:
```bash
python main.py schedule --platform facebook --type photo --time "2024-01-15T10:00:00" --content '{"image_path": "path/to/image.jpg", "message": "Check out this image!"}'
```

**YouTube Video**:
```bash
python main.py schedule --platform youtube --type video --time "2024-01-15T10:00:00" --content '{"video_path": "path/to/video.mp4", "title": "My Video", "description": "Video description", "tags": ["tag1", "tag2"], "privacy_status": "public"}'
```

**LinkedIn Text Post**:
```bash
python main.py schedule --platform linkedin --type text --time "2024-01-15T10:00:00" --content '{"text": "Hello LinkedIn!"}'
```

**LinkedIn Image Post**:
```bash
python main.py schedule --platform linkedin --type image --time "2024-01-15T10:00:00" --content '{"text": "Check this out!", "image_path": "path/to/image.jpg"}'
```

**Instagram Carousel**:
```bash
python main.py schedule --platform instagram --type carousel --time "2024-01-15T10:00:00" --content '{"image_paths": ["img1.jpg", "img2.jpg", "img3.jpg"], "caption": "Carousel post!"}'
```

### Run the Scheduler

Start the scheduler to automatically post scheduled content:

```bash
python main.py run
```

The scheduler will:
- Check for scheduled posts every 60 seconds (configurable in `config.yaml`)
- Execute posts when their scheduled time arrives
- Save post status and results

### List Scheduled Posts

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

## Project Structure

```
.
├── main.py                 # CLI entry point
├── scheduler.py            # Unified scheduler
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── platforms/
│   ├── __init__.py
│   ├── instagram.py       # Instagram automation
│   ├── facebook.py        # Facebook automation
│   ├── youtube.py         # YouTube automation
│   └── linkedin.py        # LinkedIn automation
├── scheduled_posts.json   # Scheduled posts database (auto-generated)
└── README.md             # This file
```

## Important Notes

### Security
- Never commit `.env`, `config.yaml`, or credential files to version control
- Keep your access tokens secure
- Use environment variables for sensitive data in production

### Rate Limits
- Each platform has rate limits. Be mindful of:
  - **Instagram**: ~100 posts per day
  - **Facebook**: Varies by account type
  - **YouTube**: 6 uploads per day (unverified accounts)
  - **LinkedIn**: Varies by account type

### Scheduling
- Scheduled times should be in ISO format: `YYYY-MM-DDTHH:MM:SS`
- Times are checked every 60 seconds by default
- Posts are executed when scheduled time arrives (within 1 minute window)

### Instagram
- First login may require manual verification
- Session is saved for future use
- Images must be at least 320x320 pixels
- Carousels support 2-10 images

### Facebook
- Requires Page Access Token (not User Access Token)
- Scheduled posts are published automatically by Facebook
- Image formats: JPG, PNG, GIF

### YouTube
- First authentication opens browser for OAuth
- Credentials are saved after first auth
- Videos must meet YouTube's requirements
- Scheduled videos are set to private until publish time

### LinkedIn
- Requires Marketing Developer Platform access
- Image upload uses multi-step process
- Text posts are immediate (LinkedIn doesn't support native scheduling)

## Troubleshooting

### Instagram Login Issues
- If you see "Challenge Required", verify your account manually
- Check if 2FA is enabled and handle it appropriately
- Session files may need to be deleted and recreated

### Facebook API Errors
- Verify your Page Access Token has correct permissions
- Check if token is expired (tokens may expire)
- Ensure Page ID is correct

### YouTube Authentication
- Make sure `client_secrets.json` is in the project root
- First run will open browser - complete OAuth flow
- Check Google Cloud Console for API quota

### LinkedIn API Errors
- Verify access token has `w_member_social` permission
- Check if Person URN format is correct
- Ensure Marketing Developer Platform access is granted

## License

This project is provided as-is for educational and personal use.

## Disclaimer

This tool automates social media posting. Please:
- Follow each platform's Terms of Service
- Respect rate limits
- Don't spam or post inappropriate content
- Use responsibly

