import asyncio
import time
import os
import re

def extract_youtube_metadata(response_text):
    """Extract YouTube metadata from Gemini response"""
    metadata = {
        'title': '',
        'description': '',
        'tags': []
    }

    # Split response into lines for better parsing
    lines = response_text.split('\n')

    for line in lines:
        line = line.strip()
        if line.upper().startswith('TITLE:'):
            # Extract everything after TITLE:
            title_text = line[6:].strip()  # Remove "TITLE:"
            # Stop at any subsequent keyword if present in the same line
            title_text = re.split(r'\bDESCRIPTION:|\bTAGS:', title_text, flags=re.IGNORECASE)[0].strip()
            metadata['title'] = title_text
        elif line.upper().startswith('DESCRIPTION:'):
            # Extract everything after DESCRIPTION:
            desc_text = line[12:].strip()  # Remove "DESCRIPTION:"
            # Stop at TAGS: if present
            desc_text = re.split(r'\bTAGS:', desc_text, flags=re.IGNORECASE)[0].strip()
            metadata['description'] = desc_text
        elif line.upper().startswith('TAGS:'):
            # Extract everything after TAGS:
            tags_text = line[5:].strip()  # Remove "TAGS:"
            # Split by comma and clean up
            metadata['tags'] = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

    return metadata

async def run_gemini_task(page, prompt, task_type, out_dir, platforms=None):
    # 1. Navigation
    await page.goto("https://gemini.google.com/", wait_until="domcontentloaded", timeout=60000)

    box_selector = "div[role='textbox']"
    await page.wait_for_selector(box_selector, timeout=30000)

    # 2. Prepare and Send Prompt
    task_type = task_type.upper()
    platforms = platforms or []

    if task_type == "IMAGE":
        prefix = "Generate an image of: "
    elif task_type == "VIDEO":
        prefix = "Generate a high-quality video of: "
        # If YouTube is in platforms, generate video with metadata
        if 'youtube' in [p.lower() for p in platforms]:
            prefix = f"""Generate a high-quality video of: {prompt}

            After generating the video, also provide:
            - TITLE: A catchy YouTube title (max 100 characters)
            - DESCRIPTION: An engaging description (max 5000 characters)
            - TAGS: 5-10 relevant tags separated by commas

            Format your response with the video first, then the metadata below."""
    elif task_type == "PPT":
        prefix = "Create a detailed PPT outline in a Markdown TABLE format for: "
    else:
        prefix = f"Create a {task_type} for: "

    await page.fill(box_selector, f"{prefix}{prompt}")
    await page.keyboard.press("Enter")
    print(f"Waiting for {task_type} generation...")

    # 3. PPT Logic (Manual Action + URL Extraction)
    if task_type == "PPT":
        print(">>> MANUAL ACTION REQUIRED: Please click 'Export to Sheets' now...")
        try:
            async with page.context.expect_page(timeout=120000) as new_page_info:
                new_sheet_tab = new_page_info.value

            print("New Sheet detected! Extracting URL...")
            final_url = ""
            for _ in range(15):
                if "docs.google.com" in new_sheet_tab.url:
                    final_url = new_sheet_tab.url
                    break
                await asyncio.sleep(1)

            final_url = final_url if final_url else new_sheet_tab.url
            print(f"Captured: {final_url}")
            await new_sheet_tab.close()
            return final_url
        except Exception as e:
            print(f"Manual capture failed: {e}")
            text_selector = "div[class*='message-content'], .model-response-text"
            await page.wait_for_selector(text_selector, timeout=10000)
            content = await page.locator(text_selector).last.inner_text()
            save_path = os.path.join(out_dir, f"PPT_Backup_{int(time.time())}.txt")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)
            return save_path

    # 4. Video Handling Logic (Robust Update)
    elif task_type == "VIDEO":
        video_selector = "video, [class*='video'], [aria-label*='video'], .video-player"
        generate_btn_selector = "button:has-text('Generate'), button:has-text('Create video')"

        try:
            await asyncio.sleep(5)
            if await page.locator(generate_btn_selector).is_visible():
                print("Clicking 'Generate' button inside Gemini...")
                await page.locator(generate_btn_selector).click()

            print("Video generation started. Waiting up to 7 minutes...")
            # state="attached" ensures we find the element even if hidden by an overlay
            await page.wait_for_selector(video_selector, timeout=420000, state="attached")

            download_btn_selector = "button[aria-label*='Download'], [mattooltip*='Download video'], button:has(mat-icon:has-text('download'))"

            # Wait for the download button to be available in the DOM
            await page.wait_for_selector(download_btn_selector, timeout=60000)

            print("Attempting to download video...")
            try:
                # force=True ignores the 'pointer-events' check that failed previously
                async with page.expect_download(timeout=120000) as download_info:
                    await page.locator(download_btn_selector).last.click(force=True)

                download = download_info.value
                save_path = os.path.join(out_dir, f"VIDEO_{int(time.time())}.mp4")
                await download.save_as(save_path)

                print(f"Saved video locally: {save_path}")

                # Check if we need to extract YouTube metadata
                if 'youtube' in [p.lower() for p in (platforms or [])]:
                    try:
                        # Extract metadata from Gemini response
                        text_selector = "div[class*='message-content'], .model-response-text"
                        await page.wait_for_selector(text_selector, timeout=5000)
                        response_text = await page.locator(text_selector).last.inner_text()

                        # Parse metadata
                        metadata = extract_youtube_metadata(response_text)
                        metadata_path = save_path.replace('.mp4', '_metadata.json')

                        import json
                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2)

                        print(f"YouTube metadata extracted and saved to: {metadata_path}")
                        return {'video_path': save_path, 'metadata': metadata}
                    except Exception as meta_err:
                        print(f"Failed to extract YouTube metadata: {meta_err}")
                        return save_path
                else:
                    return save_path

            except Exception as download_err:
                print(f"Standard download failed, trying direct URL capture...")
                # FALLBACK: Directly grab the video source URL
                video_src = await page.locator("video").first.get_attribute("src")
                if video_src:
                    print(f"Captured Direct Video URL: {video_src}")
                    return video_src
                raise download_err

        except Exception as e:
            error_img = os.path.join(out_dir, "video_error.png")
            await page.screenshot(path=error_img)
            print(f"Video failed. See screenshot: {error_img}")
            raise Exception(f"Video processing failed: {e}")

    # 5. Image Handling Logic (Fully Automated)
    elif task_type == "IMAGE":
        image_selector = "img[class*='image'][class*='loaded']"
        try:
            await page.wait_for_selector(image_selector, timeout=150000)
            print("Image content detected.")

            download_btn = "button[aria-label*='Download'], [mattooltip*='Download']"
            await asyncio.sleep(5)

            await page.locator(image_selector).first.hover()

            async with page.expect_download(timeout=60000) as download_info:
                await page.locator(download_btn).first.click(force=True)

            download = await download_info.value
            save_path = os.path.join(out_dir, f"IMAGE_{int(time.time())}.png")
            await download.save_as(save_path)

            print(f"Saved image locally: {save_path}")
            return save_path

        except Exception as e:
            await page.screenshot(path=os.path.join(out_dir, "image_error.png"))
            raise Exception(f"Image download failed: {e}")                                                                                                                            