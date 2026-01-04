"""
Update Postman collection with current LinkedIn credentials from constants
"""
import json
import re

def get_constants_values():
    """Get values from linkedin_constants.py"""
    try:
        from linkedin_constants import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN
        return {
            'token': LINKEDIN_ACCESS_TOKEN,
            'urn': LINKEDIN_PERSON_URN
        }
    except ImportError:
        print("[ERROR] Could not import linkedin_constants.py")
        return None

def update_postman_collection():
    """Update Postman collection with current values"""
    values = get_constants_values()
    if not values:
        return False
    
    try:
        with open('linkedin_postman_collection.json', 'r') as f:
            collection = json.load(f)
        
        # Update token in all requests
        token = values['token']
        urn = values['urn']
        
        def update_request(request):
            """Update a request with new token and URN"""
            if 'header' in request:
                for header in request['header']:
                    if header.get('key') == 'Authorization':
                        header['value'] = f"Bearer {token}"
            
            if 'body' in request and 'raw' in request['body']:
                # Update URN in body
                body = request['body']['raw']
                # Replace URN
                body = re.sub(r'"author":\s*"[^"]*"', f'"author": "{urn}"', body)
                body = re.sub(r'"owner":\s*"[^"]*"', f'"owner": "{urn}"', body)
                request['body']['raw'] = body
        
        # Update all items
        if 'item' in collection:
            for item in collection['item']:
                if 'request' in item:
                    update_request(item['request'])
                elif 'item' in item:  # Nested items
                    for sub_item in item['item']:
                        if 'request' in sub_item:
                            update_request(sub_item['request'])
        
        # Update variables
        if 'variable' in collection:
            for var in collection['variable']:
                if var.get('key') == 'linkedin_token':
                    var['value'] = token
                elif var.get('key') == 'linkedin_urn':
                    var['value'] = urn
        
        # Save updated collection
        with open('linkedin_postman_collection.json', 'w') as f:
            json.dump(collection, f, indent=2)
        
        print("[OK] Updated linkedin_postman_collection.json")
        print(f"     Token: {token[:30]}...")
        print(f"     URN: {urn}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Could not update Postman collection: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("  UPDATE POSTMAN COLLECTION")
    print("=" * 70)
    print("\nUpdating Postman collection with current LinkedIn credentials...\n")
    update_postman_collection()
    print("\n" + "=" * 70)
    print("Done! Import linkedin_postman_collection.json into Postman.")
    print("=" * 70)

