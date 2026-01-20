import pandas as pd

def get_tasks_from_excel(file_path):
    try:
        # 1. Load the file
        df = pd.read_excel(file_path)
        
        # 2. Clean up column names: remove spaces and make them Title Case
        # This makes "  prompt  " -> "Prompt"
        df.columns = [str(c).strip().title() for c in df.columns]
        
        # 3. Check if the required columns actually exist
        required_columns = ['Prompt', 'Type']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing column in Excel: '{col}'")
        
        # 4. Filter and convert to list of dictionaries
        tasks = df[required_columns].dropna(how='all').to_dict('records')
        
        print(f"Successfully loaded {len(tasks)} tasks.")
        return tasks
        
    except Exception as e:
        print(f"Excel Error: {e}")
        return []