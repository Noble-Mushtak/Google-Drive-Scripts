from googleapiclient.discovery import build
from utilities import *

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive"]

def main():
    # Get the user's credentials:
    creds = get_credentials(SCOPES)
            
    # Initialize the Drive v3 API
    service = build("drive", "v3", credentials=creds)
    print("For the following prompts, the \""+root_folder_name+"\" folder is assumed to be the root file of your Google Drive.")
    
    # Get the folder name from the user:
    orig_folder_name = input("Enter the name of the folder you want to copy: ")
    orig_folder = get_folder(service, orig_folder_name)
    if orig_folder == None:
        return
    
    new_folder_name = input("Enter the name of the folder you want the copy to end up in: ")
    new_folder = get_folder(service, new_folder_name)
    if new_folder == None:
        return
    
    copy_folder(service, orig_folder, new_folder)
        
def begin_copying(drive_service, folder, new_folder):
    print("Started copying folder", folder.get("name"))
    # Create a copy of the folder:
    metadata = {
        "name": folder.get("name"),
        "mimeType": folder_mime_type,
        "parents": [new_folder.get("id")]
    }
    folder_copy = drive_service.files().create(body=metadata, fields="id, name, mimeType").execute()
    # Use folder_copy as additional argument:
    return (folder_copy,)

def end_copying(folder, total):
    print("Finished copying folder", folder.get("name"))

@recurse_folder(begin_copying, end_copying)
def copy_folder(drive_service, file, new_folder, folder_copy):
    # Make a recursive call if this file is a folder:
    if file.get("mimeType") == folder_mime_type:
        copy_folder(drive_service, file, folder_copy)
    # Otherwise, just make a normal copy by copying the file and putting it in the right folder:
    else:
        metadata = {
            "name": file.get("name"),
            "parents": [folder_copy.get("id")]
        }
        new_file = drive_service.files().copy(body=metadata, fileId=file.get("id"), fields="id, name, mimeType").execute()
        print("Copied file", file.get("name"))
    # Return value is ignored, so just return 0:
    return 0

if __name__ == "__main__":
    main()