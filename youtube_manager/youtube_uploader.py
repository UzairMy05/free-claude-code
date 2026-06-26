import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes required for YouTube uploads
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_service(
    client_secrets_path="client_secrets.json", token_path="token.pickle"
):
    """
    Authenticates the user and returns the YouTube API service object.
    Stores user credentials in token.pickle for subsequent runs.
    """
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_path):
                raise FileNotFoundError(
                    f"Please download '{client_secrets_path}' from Google Cloud Console "
                    "and place it in the same directory as this script."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, SCOPES
            )
            # Run local server for authentication
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)


def upload_short(youtube, video_path, title, description, tags=None):
    """
    Uploads a video to YouTube and sets it as 'Made for Kids' and public.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    body = {
        "snippet": {
            "title": title[:100],  # Title limit is 100 characters
            "description": description[:5000],  # Description limit is 5000
            "tags": tags or [],
            "categoryId": "27",  # Education category
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True,  # Critical for COPPA compliance (target: kids <= 12)
        },
    }

    # Upload media object
    media = MediaFileUpload(
        video_path, mimetype="video/mp4", chunksize=1024 * 1024, resumable=True
    )

    print(f"Uploading {video_path}...")
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%...")

    print(f"Upload complete! Video ID: {response.get('id')}")
    return response.get("id")


if __name__ == "__main__":
    # Test script entrypoint
    try:
        service = get_youtube_service()
        print("Successfully authenticated with YouTube Data API!")
    except Exception as e:
        print(f"Authentication failed: {e}")
