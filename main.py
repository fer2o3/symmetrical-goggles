import requests
import os


class StravaCommitUpdater:
    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None

    def refresh_access_token(self):
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
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            return False

    def get_last_activities(self, count=30):
        if not self.access_token:
            if not self.refresh_access_token():
                return None

        headers = {'Authorization': f'Bearer {self.access_token}'}

        try:
            response = requests.get(
                'https://www.strava.com/api/v3/athlete/activities',
                headers=headers,
                params={
                    'per_page': count  # Get exactly the number we want
                }
            )
            print(f"Activities response status: {response.status_code}")
            response.raise_for_status()

            activities = response.json()
            return activities

        except requests.exceptions.RequestException as e:
            print(f"Error fetching activities: {e}")
            return None

    def get_random_commit_message(self):
        try:
            response = requests.get('https://whatthecommit.com/index.txt')
            response.raise_for_status()
            return response.text.strip()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commit message: {e}")
            return None

    def update_activity_title(self, activity_id, new_title):
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

    def update_last_activities(self, count=30):
        activities = self.get_last_activities(count)
        if not activities:
            print("this shouldn't happen but hey you never know")
            return

        for i, activity in enumerate(activities, 1):
            commit_message = self.get_random_commit_message()
            if not commit_message:
                print("problem with whatthecommit, skipping")
                continue

            if not self.update_activity_title(activity['id'], commit_message):
                print("Fuck.")

        print("\nFinished updating activities!")


def main():
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')

    if not all([client_id, client_secret, refresh_token]):
        print("Missing required environment variables!")
        return

    updater = StravaCommitUpdater(client_id, client_secret, refresh_token)
    updater.update_last_activities(30)


if __name__ == "__main__":
    main()
