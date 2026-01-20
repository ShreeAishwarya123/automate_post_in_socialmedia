#!/usr/bin/env python3
"""
Update Excel captions with meaningful text
"""

import pandas as pd
import os

def update_captions():
    excel_path = 'gemini_automation/gemini_automation/prompts.xlsx'

    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found")
        return

    try:
        df = pd.read_excel(excel_path)
        print(f"Found {len(df)} rows in Excel")

        # Sample captions based on prompts
        for idx, row in df.iterrows():
            prompt = str(row.get('Prompt', '')).lower()

            # Generate meaningful captions
            if 'sunset' in prompt or 'mountain' in prompt:
                caption = "🌅 Witnessing the beauty of nature's masterpiece! #NatureLover #SunsetVibes"
            elif 'city' in prompt or 'cyberpunk' in prompt:
                caption = "🏙️ Exploring futuristic worlds created by AI! #Cyberpunk #FutureTech"
            elif 'retriever' in prompt or 'dog' in prompt or 'golden' in prompt:
                caption = "🐕 Man's best friend in the skies! 🐶 #DogLovers #GoldenRetriever"
            elif 'eden' in prompt or 'garden' in prompt:
                caption = "🌿 A glimpse of paradise in the Garden of Eden 🌳 #BiblicalStories #Paradise"
            elif 'red sea' in prompt or 'moses' in prompt:
                caption = "🌊 The miraculous parting of the Red Sea! ✨ #BiblicalMiracles #Faith"
            elif 'watercolor' in prompt or 'painting' in prompt:
                caption = "🎨 AI brings watercolor dreams to life! 🌈 #DigitalArt #Watercolor"
            else:
                caption = f"🤖 AI-generated content: {str(row.get('Prompt', ''))[:50]}... #AIArt #GeneratedContent"

            df.at[idx, 'Caption'] = caption
            print(f"Row {idx}: {caption[:60]}...")

        # Save
        df.to_excel(excel_path, index=False)
        print("\n[OK] Excel updated with meaningful captions!")
        print(f"Saved to: {excel_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_captions()