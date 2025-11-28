"""
Calendar Integration

Google Calendar API integration for interview scheduling.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pickle
import os
import logging

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarService:
    """Google Calendar integration service"""
    
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        # Token file stores user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no valid credentials, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
        logger.info("Calendar service authenticated successfully")
    
    def get_available_slots(
        self, 
        calendar_id: str, 
        start_date: datetime, 
        end_date: datetime,
        duration_minutes: int = 60
    ) -> List[Dict[str, datetime]]:
        """Get available time slots from calendar"""
        try:
            # Get busy times
            body = {
                "timeMin": start_date.isoformat() + 'Z',
                "timeMax": end_date.isoformat() + 'Z',
                "items": [{"id": calendar_id}]
            }
            
            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars'][calendar_id]['busy']
            
            # Generate available slots
            available_slots = []
            current_time = start_date
            
            while current_time < end_date:
                # Only consider working hours (9 AM - 5 PM)
                if 9 <= current_time.hour < 17:
                    slot_end = current_time + timedelta(minutes=duration_minutes)
                    
                    # Check if slot overlaps with any busy time
                    is_available = True
                    for busy in busy_times:
                        busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                        busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                        
                        if (current_time < busy_end and slot_end > busy_start):
                            is_available = False
                            break
                    
                    if is_available:
                        available_slots.append({
                            'start': current_time,
                            'end': slot_end
                        })
                
                # Move to next 30-minute slot
                current_time += timedelta(minutes=30)
            
            logger.info(f"Found {len(available_slots)} available slots")
            return available_slots
            
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return []
    
    def create_event(
        self, 
        calendar_id: str, 
        event_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a calendar event"""
        try:
            event = {
                'summary': event_details['summary'],
                'description': event_details.get('description', ''),
                'start': {
                    'dateTime': event_details['start'].isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': event_details['end'].isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': event_details.get('attendees', []),
                'conferenceData': event_details.get('conferenceData'),
            }
            
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                conferenceDataVersion=1
            ).execute()
            
            logger.info(f"Event created: {event.get('htmlLink')}")
            return event
            
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            raise
    
    def update_event(
        self,
        calendar_id: str,
        event_id: str,
        event_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            if 'summary' in event_details:
                event['summary'] = event_details['summary']
            if 'description' in event_details:
                event['description'] = event_details['description']
            if 'start' in event_details:
                event['start'] = {
                    'dateTime': event_details['start'].isoformat(),
                    'timeZone': 'UTC',
                }
            if 'end' in event_details:
                event['end'] = {
                    'dateTime': event_details['end'].isoformat(),
                    'timeZone': 'UTC',
                }
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Event updated: {updated_event.get('htmlLink')}")
            return updated_event
            
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            raise
    
    def delete_event(self, calendar_id: str, event_id: str):
        """Delete a calendar event"""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Event deleted: {event_id}")
            
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            raise