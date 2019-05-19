import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def get_credentials(SCOPES):
    creds = None
    # If token.pickle exists, then load the saved credentials from the pickle file:
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server()
        # Save the credentials in token.pickle for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    # Finally, return the credentials
    return creds
    
if __name__ == "__main__":
    print("Client ID:", get_credentials(["https://www.googleapis.com/auth/drive"]).client_id)