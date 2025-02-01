import requests
import os

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

    def get_last_runs(self, count=30):
        """Get the last 'count' running activities."""
        if not self.access_token:
            if not self.refresh_access_token():
                return None

        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        print(f"Fetching last {count} running activities...")
        
        try:
            # We'll fetch a bit more than needed to ensure we get enough runs
            # as some activities might not be runs
            response = requests.get(
                'https://www.strava.com/api/v3/athlete/activities',
                headers=headers,
                params={
                    'per_page': 100  # Maximum allowed by Strava API
                }
            )
            print(f"Activities response status: {response.status_code}")
            response.raise_for_status()
            
            all_activities = response.json()
            
            # Filter for runs only
            runs = [activity for activity in all_activities 
                   if activity['type'] == 'Run'][:count]
            
            print(f"Found {len(runs)} running activities")
            return runs
            
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

    def update_last_runs(self, count=30):
        """Update titles of last 'count' running activities."""
        runs = self.get_last_runs(count)
        if not runs:
            print("No running activities found or error occurred")
            return

        print(f"\nUpdating {len(runs)} running activities...")
        success_count = 0

        for i, activity in enumerate(runs, 1):
            commit_message = self.get_random_commit_message()
            if not commit_message:
                print("Failed to get commit message, skipping activity")
                continue

            print(f"\nUpdating run {i}/{len(runs)}")
            print(f"Old name: {activity['name']}")
            print(f"New name: {commit_message}")
            
            if self.update_activity_title(activity['id'], commit_message):
                success_count += 1
                print("✓ Successfully updated")
            else:
                print("✗ Failed to update")

        print(f"\nFinished updating runs!")
        print(f"Successfully updated {success_count} out of {len(runs)} activities")

def main():
    # Get credentials from environment variables
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("Missing required environment variables!")
        print("Please make sure STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and STRAVA_REFRESH_TOKEN are set")
        return

    updater = StravaCommitUpdater(client_id, client_secret, refresh_token)
    updater.update_last_runs(30)

if __name__ == "__main__":
    main()
