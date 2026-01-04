# Sample Media Files Guide

## 📸 Sample Image Created

**File:** `sample_image.jpg`
- Size: 1080x1080 pixels (Instagram/Facebook/LinkedIn compatible)
- Format: JPEG
- Ready to use for testing!

### Test with Sample Image

```bash
# LinkedIn
python post_linkedin.py "Test post with sample image!" --image sample_image.jpg

# Facebook
python post_facebook.py "Test post!" --image sample_image.jpg

# Instagram
python post_instagram.py "Test caption!" --image sample_image.jpg

# All platforms
python post_all_platforms.py "Test from all platforms!" --image sample_image.jpg
```

---

## 🎥 Sample Video

### Option 1: Use Existing Video

If you have any `.mp4` file, you can use it:

```bash
python post_youtube.py "My Video Title" --video your_video.mp4
```

### Option 2: Create Video with FFmpeg

1. **Install FFmpeg:**
   - Windows: Download from https://ffmpeg.org/download.html
   - Or use: `choco install ffmpeg` (if you have Chocolatey)
   - Or use: `winget install ffmpeg`

2. **Create Sample Video:**
   ```bash
   ffmpeg -f lavfi -i color=c=blue:size=1280x720:duration=10 -vf "drawtext=text='Sample Video':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" -c:v libx264 sample_video.mp4
   ```

3. **Test with Video:**
   ```bash
   python post_youtube.py "Sample Video" --video sample_video.mp4
   ```

### Option 3: Use Online Video Generator

- Use any online video creation tool
- Export as MP4
- Use the file for testing

---

## 🖼️ Create More Sample Images

Run the script again to create more images:

```bash
python create_sample_media.py
```

Or create custom images using Python:

```python
from PIL import Image, ImageDraw, ImageFont

# Create image
img = Image.new('RGB', (1080, 1080), color='#4A90E2')
draw = ImageDraw.Draw(img)

# Add text
text = "Your Custom Text"
draw.text((540, 540), text, fill='white')

# Save
img.save('custom_image.jpg')
```

---

## ✅ Quick Test Commands

**With Sample Image:**
```bash
# Test LinkedIn
python post_linkedin.py "Testing with sample image!" --image sample_image.jpg

# Test Facebook
python post_facebook.py "Testing!" --image sample_image.jpg

# Test Instagram
python post_instagram.py "Test caption #testing" --image sample_image.jpg

# Test All
python post_all_platforms.py "Testing all platforms!" --image sample_image.jpg
```

**With Your Own Video:**
```bash
python post_youtube.py "My Test Video" --video your_video.mp4 --description "Test description" --tags test video
```

---

## 📋 File Requirements

### Image Requirements
- **Instagram**: Minimum 320x320, recommended 1080x1080
- **Facebook**: JPG, PNG, GIF
- **LinkedIn**: JPG, PNG

### Video Requirements
- **YouTube**: MP4, MOV, AVI
- Recommended: 1280x720 or 1920x1080
- Max file size: 128GB (but smaller is better)

---

**Sample image is ready! Use it to test your posts!** ✅

