# Project Structure

## 📁 Essential Files

```
.
├── COMPLETE_GUIDE.md              # Complete guide (READ THIS FIRST!)
├── README.md                      # Quick overview
├── main.py                        # Main scheduler CLI
├── scheduler.py                   # Scheduler engine
├── post_all_platforms.py          # Post to all platforms
├── post_linkedin.py               # Post to LinkedIn only
├── linkedin_constants.py          # LinkedIn credentials (update here)
├── sync_linkedin_config.py        # Sync LinkedIn constants to config
├── update_postman_collection.py   # Update Postman collection
├── config.yaml                    # Platform configuration
├── linkedin_postman_collection.json  # Postman collection
├── requirements.txt               # Python dependencies
├── platforms/                     # Platform modules
│   ├── __init__.py
│   ├── instagram.py
│   ├── facebook.py
│   ├── youtube.py
│   └── linkedin.py
└── scheduled_posts.json           # Scheduled posts (auto-generated)
```

## 🚀 Quick Start

1. Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
2. Install: `pip install -r requirements.txt`
3. Configure: Edit `config.yaml`
4. Post: `python post_all_platforms.py "Hello!"`

## 📖 Documentation

- **COMPLETE_GUIDE.md** - Full guide with all instructions
- **README.md** - Quick overview

