#!/usr/bin/env python3
"""
Setup Google Calendar API authentication

This script helps you authenticate with Google Calendar API and save credentials
for future use by the Interview Scheduler Agent.

Prerequisites:
1. Create a project in Google Cloud Console
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json and place it in project root

Run this script once to authenticate and generate token.pickle
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle

# If modifying these scopes, delete the token.pickle file
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def setup_calendar_auth():
    """Setup Google Calendar API authentication"""
    
    print("=" * 70)
    print("Google Calendar API Authentication Setup")
    print("=" * 70)
    print()
    
    # Check if credentials.json exists
    credentials_path = project_root / 'credentials.json'
    token_path = project_root / 'token.pickle'
    
    if not credentials_path.exists():
        print("❌ ERROR: credentials.json not found!")
        print()
        print("Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing project")
        print("3. Enable Google Calendar API")
        print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'")
        print("5. Choose 'Desktop app' as application type")
        print("6. Download the credentials JSON file")
        print("7. Rename it to 'credentials.json'")
        print("8. Place it in the project root directory")
        print()
        return False
    
    print("✓ Found credentials.json")
    print()
    
    creds = None
    
    # Check if token already exists
    if token_path.exists():
        print("Found existing token.pickle")
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        print("✓ Loaded existing credentials")
    
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expired. Refreshing...")
            try:
                creds.refresh(Request())
                print("✓ Token refreshed successfully")
            except Exception as e:
                print(f"❌ Failed to refresh token: {e}")
                print("Please re-authenticate...")
                creds = None
        
        if not creds:
            print()
            print("=" * 70)
            print("AUTHENTICATION REQUIRED")
            print("=" * 70)
            print()
            print("A browser window will open for you to authenticate.")
            print("Please log in with your Google account and grant permissions.")
            print()
            input("Press ENTER to continue...")
            print()
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), 
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
                print()
                print("✓ Authentication successful!")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return False
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print(f"✓ Credentials saved to {token_path}")
    
    print()
    print("=" * 70)
    print("TESTING CONNECTION")
    print("=" * 70)
    print()
    
    # Test the connection
    try:
        from googleapiclient.discovery import build
        
        service = build('calendar', 'v3', credentials=creds)
        
        # Get list of calendars
        print("Fetching your calendars...")
        calendar_list = service.calendarList().list().execute()
        
        print()
        print("✓ Successfully connected to Google Calendar!")
        print()
        print("Your calendars:")
        print("-" * 70)
        
        for calendar in calendar_list.get('items', []):
            primary = " (PRIMARY)" if calendar.get('primary', False) else ""
            print(f"  • {calendar['summary']}{primary}")
            print(f"    ID: {calendar['id']}")
        
        print()
        print("=" * 70)
        print("✅ SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("You can now use the Interview Scheduler Agent.")
        print("The token.pickle file will be used for authentication.")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print()
        print("Please check:")
        print("1. Google Calendar API is enabled in your project")
        print("2. Your credentials have the correct permissions")
        print("3. You have internet connectivity")
        return False

def revoke_credentials():
    """Revoke and delete existing credentials"""
    token_path = project_root / 'token.pickle'
    
    if token_path.exists():
        print("Deleting token.pickle...")
        os.remove(token_path)
        print("✓ Credentials revoked")
    else:
        print("No credentials found to revoke")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Setup Google Calendar API authentication'
    )
    parser.add_argument(
        '--revoke',
        action='store_true',
        help='Revoke existing credentials and re-authenticate'
    )
    
    args = parser.parse_args()
    
    if args.revoke:
        print("Revoking credentials...")
        revoke_credentials()
        print()
    
    success = setup_calendar_auth()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()