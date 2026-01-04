# Individual Platform Posting Commands

## 📋 Quick Reference - Post to Each Platform Separately

---

## 1. LinkedIn

### Text Post
```bash
python post_linkedin.py "Hello LinkedIn!"
```

### Image Post
```bash
python post_linkedin.py "Check this out!" --image photo.jpg
```

---

## 2. Facebook

### Text Post
```bash
python post_facebook.py "Hello Facebook!"
```

### Image Post
```bash
python post_facebook.py "Check this out!" --image photo.jpg
```

---

## 3. Instagram

### Single Photo Post
```bash
python post_instagram.py "My awesome caption!" --image photo.jpg
```

### Carousel Post (2-10 images)
```bash
python post_instagram.py "Carousel caption!" --images img1.jpg img2.jpg img3.jpg
```

**Note:** Instagram requires an image (cannot post text-only)

---

## 4. YouTube

### Basic Video Upload
```bash
python post_youtube.py "My Video Title" --video video.mp4
```

### Video with Description
```bash
python post_youtube.py "My Video Title" --video video.mp4 --description "Video description here"
```

### Video with Tags
```bash
python post_youtube.py "My Video Title" --video video.mp4 --tags tech tutorial programming
```

### Complete Video Upload
```bash
python post_youtube.py "My Video Title" --video video.mp4 --description "Video description" --tags tech tutorial --privacy public
```

**Privacy options:** `public`, `unlisted`, `private`

---

## 📝 Examples

### LinkedIn Examples
```bash
# Text only
python post_linkedin.py "Excited to share my latest project!"

# With image
python post_linkedin.py "Check out this amazing design!" --image design.jpg
```

### Facebook Examples
```bash
# Text only
python post_facebook.py "Hello everyone! How's your day?"

# With image
python post_facebook.py "Beautiful sunset today!" --image sunset.jpg
```

### Instagram Examples
```bash
# Single photo
python post_instagram.py "Love this view! #nature #photography" --image view.jpg

# Carousel
python post_instagram.py "Project showcase!" --images img1.jpg img2.jpg img3.jpg img4.jpg
```

### YouTube Examples
```bash
# Basic upload
python post_youtube.py "Python Tutorial - Part 1" --video tutorial.mp4

# Complete upload
python post_youtube.py "Python Tutorial - Part 1" --video tutorial.mp4 --description "Learn Python basics in this tutorial" --tags python programming tutorial --privacy public
```

---

## ⚠️ Important Notes

### File Paths
- Use absolute paths: `C:\Users\YourName\Desktop\photo.jpg`
- Or relative paths: `photo.jpg` (if in same directory)

### Platform Requirements
- **LinkedIn**: Text or image
- **Facebook**: Text or image
- **Instagram**: Requires image (photo or carousel)
- **YouTube**: Requires video

### Error Handling
- If a post fails, check your credentials in `config.yaml`
- Verify file paths are correct
- Check platform is enabled in `config.yaml`

---

## 🔄 Alternative: Post to All Platforms

To post to all platforms at once:
```bash
python post_all_platforms.py "Hello from all platforms!" --image photo.jpg
```

To post to specific platforms only:
```bash
python post_all_platforms.py "Hello!" --platforms facebook linkedin
```

---

**All commands are ready to use!** ✅

