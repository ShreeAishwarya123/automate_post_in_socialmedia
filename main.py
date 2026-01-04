"""
Main entry point for Social Media Automation
Provides CLI interface for scheduling posts
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from scheduler import SocialMediaScheduler

def main():
    parser = argparse.ArgumentParser(description='Social Media Post Automation and Scheduling')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration file')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a post')
    schedule_parser.add_argument('--platform', required=True, 
                                choices=['instagram', 'facebook', 'youtube', 'linkedin'],
                                help='Platform to post to')
    schedule_parser.add_argument('--type', required=True,
                                choices=['photo', 'text', 'video', 'carousel', 'image'],
                                help='Type of post')
    schedule_parser.add_argument('--time', required=True,
                                help='Scheduled time in ISO format (e.g., 2024-01-15T10:00:00)')
    schedule_parser.add_argument('--content', required=True,
                                help='JSON string with post content')
    
    # Run scheduler command
    run_parser = subparsers.add_parser('run', help='Run the scheduler')
    
    # List scheduled posts
    list_parser = subparsers.add_parser('list', help='List scheduled posts')
    list_parser.add_argument('--status', choices=['scheduled', 'posted', 'failed', 'all'],
                            default='all', help='Filter by status')
    
    # Test platform
    test_parser = subparsers.add_parser('test', help='Test platform connection')
    test_parser.add_argument('--platform', required=True,
                            choices=['instagram', 'facebook', 'youtube', 'linkedin'],
                            help='Platform to test')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    scheduler = SocialMediaScheduler(args.config)
    
    if args.command == 'schedule':
        try:
            content = json.loads(args.content)
            success = scheduler.schedule_post(
                args.platform,
                args.type,
                content,
                args.time
            )
            if success:
                print(f"[OK] Post scheduled successfully for {args.platform} at {args.time}")
            else:
                print(f"[ERROR] Failed to schedule post")
                sys.exit(1)
        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON in --content parameter")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            sys.exit(1)
    
    elif args.command == 'run':
        scheduler.run()
    
    elif args.command == 'list':
        posts = scheduler.scheduled_posts
        
        if args.status != 'all':
            posts = [p for p in posts if p.get('status') == args.status]
        
        if not posts:
            print("No posts found")
        else:
            print(f"\nFound {len(posts)} post(s):\n")
            for post in posts:
                print(f"ID: {post['id']}")
                print(f"Platform: {post['platform']}")
                print(f"Type: {post['post_type']}")
                print(f"Scheduled: {post['scheduled_time']}")
                print(f"Status: {post['status']}")
                if 'posted_at' in post:
                    print(f"Posted: {post['posted_at']}")
                if 'error' in post:
                    print(f"Error: {post['error']}")
                print("-" * 50)
    
    elif args.command == 'test':
        if args.platform not in scheduler.platforms:
            print(f"[ERROR] Platform {args.platform} not initialized or not available")
            sys.exit(1)
        
        platform = scheduler.platforms[args.platform]
        if hasattr(platform, 'validate_credentials'):
            if platform.validate_credentials():
                print(f"[OK] {args.platform} connection successful")
            else:
                print(f"[ERROR] {args.platform} connection failed")
                sys.exit(1)
        else:
            print(f"[OK] {args.platform} initialized")
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()

