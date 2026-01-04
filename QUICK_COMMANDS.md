# Quick Commands Reference

## 🚀 Post to Individual Platforms

### LinkedIn

**Text Post:**
```bash
python post_linkedin.py "Hello LinkedIn!"
```

**Image Post:**
```bash
python post_linkedin.py "Check this out!" --image photo.jpg
```

---

### Facebook

**Text Post:**
```bash
python post_facebook.py "Hello Facebook!"
```

**Image Post:**
```bash
python post_facebook.py "Check this out!" --image photo.jpg
```

---

### Instagram

**Single Photo:**
```bash
python post_instagram.py "My awesome caption!" --image photo.jpg
```

**Carousel (2-10 images):**
```bash
python post_instagram.py "Carousel caption!" --images img1.jpg img2.jpg img3.jpg
```

---

### YouTube

**Basic Upload:**
```bash
python post_youtube.py "My Video Title" --video video.mp4
```

**With Description:**
```bash
python post_youtube.py "My Video Title" --video video.mp4 --description "Video description"
```

**With Tags:**
```bash
python post_youtube.py "My Video Title" --video video.mp4 --tags tech tutorial programming
```

**Complete Upload:**
```bash
python post_youtube.py "My Video Title" --video video.mp4 --description "Description" --tags tech tutorial --privacy public
```

---

## 📱 Post to All Platforms

**Text to All:**
```bash
python post_all_platforms.py "Hello from all platforms!"
```

**Image to All:**
```bash
python post_all_platforms.py "Check this out!" --image photo.jpg
```

**Specific Platforms:**
```bash
python post_all_platforms.py "Hello!" --platforms facebook linkedin
```

---

## 📅 Schedule Posts

**LinkedIn Text:**
```bash
python main.py schedule --platform linkedin --type text --time "2024-01-15T10:00:00" --content '{"text": "Hello!"}'
```

**Facebook Text:**
```bash
python main.py schedule --platform facebook --type text --time "2024-01-15T10:00:00" --content '{"message": "Hello!"}'
```

**Instagram Photo:**
```bash
python main.py schedule --platform instagram --type photo --time "2024-01-15T10:00:00" --content '{"image_path": "photo.jpg", "caption": "My post!"}'
```

**YouTube Video:**
```bash
python main.py schedule --platform youtube --type video --time "2024-01-15T10:00:00" --content '{"video_path": "video.mp4", "title": "My Video", "description": "Description", "tags": ["tag1"], "privacy_status": "public"}'
```

---

## 🔧 Other Commands

**Test Platform:**
```bash
python main.py test --platform linkedin
```

**List Scheduled Posts:**
```bash
python main.py list
```

**Run Scheduler:**
```bash
python main.py run
```

---

**For complete guide, see [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)**
