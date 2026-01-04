"""
Sync LinkedIn credentials between linkedin_constants.py and config.yaml
Ensures both files have the same values
"""
import yaml
import re

def get_constants_values():
    """Get values from linkedin_constants.py"""
    try:
        from linkedin_constants import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN
        return {
            'access_token': LINKEDIN_ACCESS_TOKEN,
            'person_urn': LINKEDIN_PERSON_URN
        }
    except ImportError:
        print("[ERROR] Could not import linkedin_constants.py")
        return None

def sync_to_config_yaml():
    """Sync constants to config.yaml"""
    print("=" * 70)
    print("  SYNC LINKEDIN CONFIG")
    print("=" * 70)
    
    # Get values from constants
    values = get_constants_values()
    if not values:
        return False
    
    print(f"\nToken: {values['access_token'][:30]}... (length: {len(values['access_token'])})")
    print(f"URN: {values['person_urn']}")
    
    # Update config.yaml
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        if 'linkedin' not in config:
            config['linkedin'] = {}
        
        config['linkedin']['access_token'] = values['access_token']
        config['linkedin']['person_urn'] = values['person_urn']
        config['linkedin']['enabled'] = True
        
        with open('config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print("\n[OK] Synced linkedin_constants.py -> config.yaml")
        print("     Both files now have the same values!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Could not update config.yaml: {e}")
        return False

if __name__ == '__main__':
    sync_to_config_yaml()

