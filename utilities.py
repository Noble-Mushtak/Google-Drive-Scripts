import functools
import operator
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Name of root folder
root_folder_name = "My Drive"
# MIME type of Google Drive folder:
folder_mime_type = "application/vnd.google-apps.folder"
# MIME type of Google Docs:
doc_mime_type = "application/vnd.google-apps.document"

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

def get_folder(drive_service, folder_name):
    # If folder is root folder, then return root:
    if folder_name == root_folder_name:
        root = drive_service.files().get(fileId="root").execute()
        return root
    
    # Search for files with that name:
    results = drive_service.files().list(
        q="name='"+folder_name+"'",
        fields="files(id, name, mimeType)"
    ).execute()
    items = results.get("files", [])
    # Remove all non-folders from the list:
    for i in range(len(items)-1, -1, -1):
        folder = items[i]
        if folder.get("mimeType") != folder_mime_type:
            del items[i]
    
    # If there are no folders, return an error:
    if len(items) == 0:
        print("No folders with that name found")
        return None
    # If there is only one folder, return that folder:
    if len(items) == 1:
        return items[0]
    # If there are multiple folders, ask the user to choose one:
    print("Multiple folders with that name found:")
    for i, folder in enumerate(items):
        print(str(i+1)+". "+folder.get("id"))
    while True:
        # Ask the user to enter a number and return the folder corresponding to that number if possible.
        folder_index = input("Select the number corresponding to the correct folder ID: ")
        try:
            folder_index = int(folder_index)
            if folder_index > 0 and folder_index <= len(items):
                return items[folder_index-1]
        except ValueError:
            pass
        print("No folder ID corresponding to that number")

def recurse_folder(begin_recursion, end_recursion, identity=0, operation=operator.add):
    '''
    Parameters:
    begin_recursion: Function which prints message and returns preliminary arguments before starting recursion
    end_recursion: Function which prints message based off return value calculated from recursion
    '''
    # Define decorator:
    def decorator(func):
        # This is the function we will ultimately return:
        @functools.wraps(func)
        def wrapper(drive_service, folder, *args):
            # Add arguments from begin_recursion so they will be passed into func later on:
            args += begin_recursion(drive_service, folder, *args)
            # This is the return value:
            total = identity
            # This stores the token for the last page:
            pageToken = None

            while pageToken != "":
                # This is the info we want from each folder:
                fields_string = "nextPageToken, files(id, size, name, mimeType)"
                # Get all of the files in this folder using the page token, if necessary:
                if pageToken == None:
                    results = drive_service.files().list(
                        q="'"+folder.get("id")+"' in parents",
                        fields=fields_string
                    ).execute()
                else:
                    results = drive_service.files().list(
                        q="'"+folder.get("id")+"' in parents",
                        pageToken=pageToken,
                        fields=fields_string
                    ).execute()
                items = results.get("files", [])
                pageToken = results.get("nextPageToken", "")
                
                # Accumulate the values of all the files in this folder:
                for file in items:
                    total = operation(
                        total, func(drive_service, file, *args)
                    )
           
            # Finally, return the total:
            total = end_recursion(drive_service, folder, total, *args)
            return total
        # The dectorator must return the wrapper
        return wrapper

    # recurse_folder must return the decorator:
    return decorator