"""
Unified Script: Generate Content with Gemini and Post to Social Media
Reads pending tasks from Excel, generates content, and posts to platforms
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime
import asyncio

# Import Gemini components
GEMINI_ROOT = os.path.join(os.path.dirname(__file__), "gemini_automation", "gemini_automation")
if GEMINI_ROOT not in sys.path:
    sys.path.insert(0, GEMINI_ROOT)

try:
    from flows.gemini_flow import run_gemini_task
    from flows.drive_flow import DriveManager
except ImportError as e:
    print(f"[ERROR] Could not import Gemini components: {e}")
    print("Make sure gemini_automation folder is properly set up")
    sys.exit(1)

# Import posting components
from post_all_platforms import post_to_all

# Configuration
EXCEL_FILE = os.path.join(GEMINI_ROOT, "prompts.xlsx")
OUTPUT_BASE_DIR = os.path.join(GEMINI_ROOT, "out")
USER_DATA_DIR = os.path.join(GEMINI_ROOT, "auth", "user_data")

async def process_pending_tasks(platforms=None, dry_run=False, prompt=None, content_type=None):
    """Process all pending tasks: generate + post"""

    # 1. Check if Excel exists
    if not os.path.exists(EXCEL_FILE):
        print(f"[ERROR] {EXCEL_FILE} not found!")
        return False

    # 2. Load Excel
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"[ERROR] Could not read Excel file: {e}")
        return False

    # Ensure status and link columns exist
    if 'Status' not in df.columns:
        df['Status'] = 'Pending'
    if 'Drive_Link' not in df.columns:
        df['Drive_Link'] = ''
    if 'Posted_Status' not in df.columns:
        df['Posted_Status'] = ''

    # 3. Check for pending tasks
    pending_df = df[df['Status'].str.lower() == 'pending']
    if pending_df.empty:
        print("[INFO] No pending tasks found in Excel")
        return True

    print(f"Found {len(pending_df)} pending task(s) to process")
    print("=" * 80)

    # 4. Initialize components
    drive = None
    if not dry_run:
        try:
            from playwright.async_api import async_playwright
            drive = DriveManager(os.path.join(GEMINI_ROOT, "auth", "credentials.json"))
        except Exception as e:
            print(f"[ERROR] Could not initialize Gemini/Drive: {e}")
            return False

    # 5. Process each pending task
    success_count = 0
    fail_count = 0

    if prompt is not None:
        # Single prompt mode
        task_type = content_type or "IMAGE"
        caption = f"AI-generated content: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"

        print(f"\n[Single] Processing: {task_type} - {prompt[:60]}{'...' if len(prompt) > 60 else ''}")

        if dry_run:
            print("  [DRY RUN] Would generate content with Gemini")
            result = f"mock_{task_type}_result"
            drive_link = "mock_drive_link"
            filtered_platforms = filter_platforms_for_content(platforms, task_type)
            print(f"  [DRY RUN] Would post to platforms: {filtered_platforms or 'none available'}")
            posting_success = True
            success_count += 1
            print("  [SUCCESS]")
        else:
            try:
                # Generate content with Gemini
                print("  Generating content with Gemini...")
                run_dir = os.path.join(OUTPUT_BASE_DIR, f"single_{int(datetime.now().timestamp())}")
                os.makedirs(run_dir, exist_ok=True)

                # Launch browser for single prompt
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    context = await p.chromium.launch_persistent_context(
                        USER_DATA_DIR,
                        headless=False,
                        args=["--disable-blink-features=AutomationControlled"]
                    )
                    page = await context.new_page()

                    result = await run_gemini_task(page, prompt, task_type, run_dir, platforms)

                    await context.close()

                if not result:
                    raise Exception("Gemini returned empty result")

                # Handle result: URL vs Local File
                drive_link = ""
                if result and str(result).startswith("http"):
                    # Direct link (PPT)
                    drive_link = result
                    print(f"  Generated link: {drive_link}")
                else:
                    # Local file - upload to Drive
                    print(f"  Uploading to Drive: {result}")
                    drive_link = drive.upload_file(result)  # Will auto-create/use folder
                    print(f"  Drive link: {drive_link}")

                # Filter platforms based on content type
                filtered_platforms = filter_platforms_for_content(platforms, task_type)
                print(f"  Posting to platforms: {filtered_platforms or 'none available'}")

                if not filtered_platforms:
                    print("  [WARNING] No suitable platforms for this content type")
                    posting_success = True  # Consider this successful since we can't post
                else:
                    posting_success = post_content_to_platforms(
                        caption, task_type, result, drive_link, filtered_platforms
                    )

                if posting_success:
                    success_count += 1
                    print("  [SUCCESS]")
                else:
                    fail_count += 1
                    print("  [POSTING FAILED]")

            except Exception as e:
                print(f"  [FAILED] {e}")
                fail_count += 1

    elif dry_run:
        # Dry run - no browser needed
        for index, row in pending_df.iterrows():
            prompt = str(row['Prompt']).strip()
            task_type = str(row['Type']).strip().upper()

            print(f"\n[{index + 1}] Processing: {task_type} - {prompt[:60]}{'...' if len(prompt) > 60 else ''}")

            # Simulate generation
            print("  [DRY RUN] Would generate content with Gemini")
            result = f"mock_{task_type}_result"

            # Simulate posting
            print(f"  [DRY RUN] Would post to platforms: {platforms or 'all'}")
            posting_success = True

            # Update Excel with simulated results
            df.at[index, 'Status'] = 'Completed'
            df.at[index, 'Posted_Status'] = f"Posted to {platforms or 'all'} (dry run)"
            success_count += 1
            print("  [SUCCESS]")
    else:
        # Real run - use browser
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await context.new_page()

            for index, row in pending_df.iterrows():
                prompt = str(row['Prompt']).strip()
                caption_raw = row.get('Caption', prompt)
                if pd.isna(caption_raw) or str(caption_raw).lower() == 'nan' or str(caption_raw).strip() == '':
                    caption = prompt  # Fall back to prompt if caption is empty/NaN
                else:
                    caption = str(caption_raw).strip()
                task_type = str(row['Type']).strip().upper()

                print(f"\n[{index + 1}] Processing: {task_type} - {prompt[:60]}{'...' if len(prompt) > 60 else ''}")

                try:
                    # Update status to Running
                    df.at[index, 'Status'] = 'Running'
                    df.to_excel(EXCEL_FILE, index=False)

                    # Generate content with Gemini
                    print("  Generating content with Gemini...")
                    run_dir = os.path.join(OUTPUT_BASE_DIR, f"task_{index + 1}")
                    os.makedirs(run_dir, exist_ok=True)

                    result = await run_gemini_task(page, prompt, task_type, run_dir, platforms)

                    if not result:
                        raise Exception("Gemini returned empty result")

                    # Handle result: URL vs Local File
                    drive_link = ""
                    if result and str(result).startswith("http"):
                        # Direct link (PPT)
                        drive_link = result
                        print(f"  Generated link: {drive_link}")
                    else:
                        # Local file - upload to Drive
                        print(f"  Uploading to Drive: {result}")
                        drive_link = drive.upload_file(result)  # Will auto-create/use folder
                        print(f"  Drive link: {drive_link}")

                    # Filter platforms based on content type
                    filtered_platforms = filter_platforms_for_content(platforms, task_type)
                    print(f"  Posting to platforms: {filtered_platforms or 'none available'}")

                    if not filtered_platforms:
                        print("  [WARNING] No suitable platforms for this content type")
                        posting_success = True  # Consider this successful since we can't post
                    else:
                        posting_success = post_content_to_platforms(
                            caption, task_type, result, drive_link, filtered_platforms
                        )

                    # Update Excel with results
                    if posting_success:
                        df.at[index, 'Status'] = 'Completed'
                        df.at[index, 'Posted_Status'] = f"Posted to {platforms or 'all'}"
                        df.at[index, 'Drive_Link'] = drive_link
                        success_count += 1
                        print("  [SUCCESS]")
                    else:
                        df.at[index, 'Status'] = 'Posted_Failed'
                        df.at[index, 'Posted_Status'] = "Posting failed"
                        df.at[index, 'Drive_Link'] = drive_link
                        fail_count += 1
                        print("  [POSTING FAILED]")

                except Exception as e:
                    print(f"  [FAILED] {e}")
                    df.at[index, 'Status'] = 'Failed'
                    df.at[index, 'Posted_Status'] = f"Error: {str(e)}"
                    fail_count += 1

                # Save progress
                try:
                    df.to_excel(EXCEL_FILE, index=False)
                except PermissionError:
                    print(f"  [WARNING] Close {EXCEL_FILE} to save progress!")

            await context.close()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tasks processed: {success_count + fail_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")

    return fail_count == 0

def post_content_to_platforms(caption, task_type, result, drive_link, platforms):
    """Post generated content to platforms"""

    # Determine posting parameters
    image_path = None
    video_path = None
    text = caption
    youtube_metadata = None

    # Handle result structure
    local_path = result
    if isinstance(result, dict) and 'video_path' in result:
        # YouTube video with metadata
        local_path = result['video_path']
        youtube_metadata = result.get('metadata', {})
        print(f"[INFO] YouTube metadata extracted: {youtube_metadata.get('title', 'N/A')}")

    if task_type == 'IMAGE' and local_path and os.path.isfile(local_path):
        image_path = local_path
    elif task_type == 'VIDEO' and local_path and os.path.isfile(local_path):
        video_path = local_path
    elif task_type == 'PPT':
        # For PPT, post the link in text
        if drive_link:
            text = f"{caption}\n\nView presentation: {drive_link}"

    # Filter platforms based on content type BEFORE posting
    filtered_platforms = filter_platforms_for_content(platforms, task_type)
    print(f"[INFO] Platforms filtered for {task_type}: {filtered_platforms}")

    if not filtered_platforms:
        print(f"[WARNING] No suitable platforms found for {task_type} content")
        return True  # Consider this successful since we can't post

    # Use YouTube metadata if available
    title = caption
    description = f"AI-generated content: {caption}"
    tags = ['AI', 'Gemini', 'Generated']

    if youtube_metadata:
        title = youtube_metadata.get('title') or title
        description = youtube_metadata.get('description') or description
        if youtube_metadata.get('tags'):
            tags = youtube_metadata['tags']

    # Post to filtered platforms
    results = post_to_all(
        text=text,
        image_path=image_path,
        video_path=video_path,
        platforms=filtered_platforms,
        title=title,
        description=description,
        tags=tags
    )

    # Check if any posting succeeded
    return any(not r.get('success', True) for r in results.values()) == False

def filter_platforms_for_content(platforms, content_type):
    """Filter platforms that can handle the given content type"""
    if not platforms:
        return platforms

    # Platform capabilities
    platform_limits = {
        'instagram': ['IMAGE', 'VIDEO'],  # Instagram supports images and videos (Reels)
        'facebook': ['IMAGE', 'VIDEO', 'PPT'],
        'youtube': ['VIDEO'],  # YouTube only supports videos
        'linkedin': ['IMAGE', 'VIDEO', 'PPT']
    }

    filtered = []
    for platform in platforms:
        platform_lower = platform.lower()
        if platform_lower in platform_limits and content_type in platform_limits[platform_lower]:
            filtered.append(platform)

    return filtered

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate content with Gemini and post to social media platforms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all pending tasks and post to all platforms
  python generate_and_post_from_excel.py

  # Process pending tasks and post only to Facebook and LinkedIn
  python generate_and_post_from_excel.py --platforms facebook linkedin

  # Dry run to see what would be processed
  python generate_and_post_from_excel.py --dry-run
        """
    )

    parser.add_argument(
        '--platforms', '-p',
        nargs='+',
        choices=['instagram', 'facebook', 'youtube', 'linkedin'],
        help='Platforms to post to (default: all enabled)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually generating or posting'
    )
    parser.add_argument(
        '--prompt',
        help='Single prompt to generate content for'
    )
    parser.add_argument(
        '--content-type',
        choices=['IMAGE', 'VIDEO', 'PPT'],
        default='IMAGE',
        help='Content type for single prompt (default: IMAGE)'
    )

    args = parser.parse_args()

    print("GEMINI CONTENT GENERATION + SOCIAL MEDIA POSTING")
    print("=" * 80)

    success = await process_pending_tasks(platforms=args.platforms, dry_run=args.dry_run, prompt=getattr(args, 'prompt', None), content_type=getattr(args, 'content_type', None))

    if success:
        print("\n[SUCCESS] All tasks completed successfully!")
    else:
        print("\n[FAILED] Some tasks failed. Check the Excel file for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())