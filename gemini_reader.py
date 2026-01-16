"""
Gemini Reader for Hive
Reads completed tasks from Gemini Automation Excel file
"""

import os
import pandas as pd
from typing import List, Dict, Optional

class GeminiReader:
    def __init__(self, excel_path="gemini_automation/gemini_automation/prompts.xlsx"):
        self.excel_path = excel_path
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

    def get_completed_tasks(self) -> List[Dict]:
        """
        Get all completed tasks with Drive links
        Returns list of dicts with: prompt, type, drive_link
        """
        try:
            df = pd.read_excel(self.excel_path)

            # Normalize column names
            df.columns = [str(c).strip().title() for c in df.columns]

            # Ensure required columns exist
            required_cols = ['Prompt', 'Type', 'Status', 'Drive_Link']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing column in Excel: {col}")

            # Filter completed tasks with valid drive links
            completed_df = df[
                (df['Status'].str.lower() == 'completed') &
                (df['Drive_Link'].notna()) &
                (df['Drive_Link'].str.strip() != '')
            ]

            tasks = []
            for _, row in completed_df.iterrows():
                tasks.append({
                    'prompt': str(row['Prompt']).strip(),
                    'type': str(row['Type']).strip().upper(),
                    'drive_link': str(row['Drive_Link']).strip()
                })

            return tasks

        except Exception as e:
            raise Exception(f"Failed to read Excel file: {e}")

    def get_tasks_by_type(self, content_type: str) -> List[Dict]:
        """
        Get completed tasks of specific type
        Args:
            content_type: 'IMAGE', 'VIDEO', or 'PPT'
        """
        all_tasks = self.get_completed_tasks()
        return [task for task in all_tasks if task['type'] == content_type.upper()]

    def get_unposted_tasks(self) -> List[Dict]:
        """
        Get completed tasks that haven't been posted yet
        (This could be extended with a 'Posted' column in Excel)
        """
        # For now, return all completed tasks
        # In future, could add 'Posted' status column
        return self.get_completed_tasks()

if __name__ == "__main__":
    # Test
    reader = GeminiReader()
    tasks = reader.get_completed_tasks()
    print(f"Found {len(tasks)} completed tasks")
    for task in tasks[:3]:  # Show first 3
        print(f"- {task['type']}: {task['prompt'][:50]}...")