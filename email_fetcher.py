import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# We only need permission to read emails for this step.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    """Authenticates with the Gmail API and returns a service object."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def fetch_and_filter_emails():
    """
    Fetches and filters emails based on subject keywords.
    """
    service = get_gmail_service()
    if not service:
        return []

    # Construct the query to filter by multiple subjects.
    filter_terms = ["Support", "Query", "Request", "Help"]
    query = " OR ".join([f"subject:({term})" for term in filter_terms])
    
    print(f"Searching for emails with query: {query}")
    
    try:
        # Get a list of messages that match the query.
        result = service.users().messages().list(userId="me", q=query).execute()
        messages = result.get("messages", [])

        if not messages:
            print("No matching emails found.")
            return []

        print(f"Found {len(messages)} matching emails. Fetching details...")
        
        email_list = []
        for msg_info in messages:
            # Get the full details of each message.
            msg = service.users().messages().get(userId="me", id=msg_info["id"]).execute()
            payload = msg.get("payload", {})
            headers = payload.get("headers", [])

            # Extract the required details from the headers.
            email_data = {
                "sender": next((h["value"] for h in headers if h["name"] == "From"), "N/A"),
                "subject": next((h["value"] for h in headers if h["name"] == "Subject"), "N/A"),
                "date": next((h["value"] for h in headers if h["name"] == "Date"), "N/A"),
                "body": ""
            }
            
            # Extract the email body (snippet is a good fallback).
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/plain":
                        if "data" in part["body"]:
                            data = part["body"]["data"]
                            email_data["body"] = base64.urlsafe_b64decode(data).decode("utf-8")
                            break
            else:
                 if "data" in payload.get("body", {}):
                    data = payload["body"]["data"]
                    email_data["body"] = base64.urlsafe_b64decode(data).decode("utf-8")

            if not email_data["body"]:
                 email_data["body"] = msg.get("snippet", "No content available.")


            email_list.append(email_data)
        
        return email_list

    except HttpError as error:
        print(f"An error occurred during email fetching: {error}")
        return []

