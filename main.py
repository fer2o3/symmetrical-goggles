import requests
import os
from datetime import datetime, timedelta
import time

class StravaCommitUpdater:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        
    def refresh_access_token(self):
        """Refresh the Strava access token using the refresh token."""
        auth_url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        print("Attempting to refresh token...")
        try:
            response = requests.post(auth_url, data=payload)
            print(f"Token refresh response status: {response.status_code}")
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data['access_token']
            print("Successfully refreshed access token")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            return False

    def get_recent_activities(self):
        """Get activities from the last 24 hours."""
        if not self.access_token:
            if not self.refresh_access_token():
                return None

        headers = {'Authorization': f'Bearer {self.access_token}'}
        after_timestamp = int((datetime.now() - timedelta(days=1)).timestamp())
        
        print(f"Fetching activities after timestamp: {after_timestamp}")
        
        try:
            response = requests.get(
                'https://www.strava.com/api/v3/athlete/activities',
                headers=headers,
                params={'after': after_timestamp}
            )
            print(f"Activities response status: {response.status_code}")
            response.raise_for_status()
            activities = response.json()
            print(f"Found {len(activities)} activities")
            return activities
        except requests.exceptions.RequestException as e:
            print(f"Error fetching activities: {e}")
            return None

    def get_random_commit_message(self):
        """Fetch a random commit message from whatthecommit.com."""
        try:
            response = requests.get('https://whatthecommit.com/index.txt')
            response.raise_for_status()
            return response.text.strip()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commit message: {e}")
            return None

    def update_activity_title(self, activity_id, new_title):
        """Update the title of a specific activity."""
        if not self.access_token:
            if not self.refresh_access_token():
                return False

        headers = {'Authorization': f'Bearer {self.access_token}'}
        update_url = f'https://www.strava.com/api/v3/activities/{activity_id}'
        
        try:
            response = requests.put(
                update_url,
                headers=headers,
                data={'name': new_title}
            )
            print(f"Update response status: {response.status_code}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error updating activity {activity_id}: {e}")
            return False

    def update_recent_activities(self):
        """Update titles of all activities from the last 24 hours."""
        activities = self.get_recent_activities()
        if not activities:
            print("No activities found or error occurred")
            return

        commit_message = self.get_random_commit_message()
        if not commit_message:
            print("Failed to get commit message")
            return

        for activity in activities:
            print(f"Updating activity {activity['id']} ({activity['name']})")
            if self.update_activity_title(activity['id'], commit_message):
                print(f"Successfully updated to: {commit_message}")
            else:
                print(f"Failed to update activity {activity['id']}")

def main():
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("Missing required environment variables!")
        print("Please make sure STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and STRAVA_REFRESH_TOKEN are set")
        return

    updater = StravaCommitUpdater(client_id, client_secret, refresh_token)
    updater.update_recent_activities()

if __name__ == "__main__":
    main()
