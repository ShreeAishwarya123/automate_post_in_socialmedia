"""
LinkedIn Constants - Centralized Configuration
Update your token and URN here - all scripts will use these values
"""

# LinkedIn Access Token
# Get from: https://www.linkedin.com/developers/tools/access-token
# Select scope: w_member_social
LINKEDIN_ACCESS_TOKEN = "AQWo36tIggjQZvyXoT6ovka4mn5xb1ascGtLfm_-HR5IU8m03l8Cf-EEqfp5LlRdF8Xow4_EwDi8qC0OWWsYQTMk58lexvTvo89wVKMpTzuqPsb97I9pvFAsPcIgE7IoFWXP0rlQXed4qQbl2A31zRI-n-Hy94jbXJp4SgEEG90KJw7o5w_NBzyuPvgPMF-32gotI07ckQFS0PgHQj3cfWTwB2EFRQTr_sV5_tBh7Emqs_xxKCO3Oh2C_cnAFvJEbTaP_7flMgw2MNT0sep1zQvva8hm3aREaBZ0x0s3R4O6Jhu7sqPuR-0Y4yGsArZ8tmoRUkJhpwvF3_SsO6W3U1Ixa9cN6Q"

# LinkedIn Person URN
# Format: urn:li:person:XXXXX or urn:li:member:XXXXX
LINKEDIN_PERSON_URN = "urn:li:person:5pPM9yKtDi"

# LinkedIn API Base URL
LINKEDIN_API_BASE_URL = "https://api.linkedin.com/v2"

# LinkedIn API Headers Template
LINKEDIN_HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

def get_linkedin_token():
    """Get LinkedIn access token"""
    return LINKEDIN_ACCESS_TOKEN

def get_linkedin_urn():
    """Get LinkedIn person URN"""
    return LINKEDIN_PERSON_URN

def get_linkedin_headers():
    """Get LinkedIn API headers"""
    return LINKEDIN_HEADERS.copy()

def update_token(new_token):
    """Update the token (for programmatic updates)"""
    global LINKEDIN_ACCESS_TOKEN, LINKEDIN_HEADERS
    LINKEDIN_ACCESS_TOKEN = new_token
    LINKEDIN_HEADERS["Authorization"] = f"Bearer {new_token}"

def update_urn(new_urn):
    """Update the URN (for programmatic updates)"""
    global LINKEDIN_PERSON_URN
    LINKEDIN_PERSON_URN = new_urn

