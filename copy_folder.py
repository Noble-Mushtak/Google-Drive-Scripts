from googleapiclient.discovery import build
from credentials import get_credentials

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive"]
# MIME type of Google Drive folder:
folder_mime_type = "application/vnd.google-apps.folder"
# Name of root folder
root_folder_name = "My Drive"

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

def get_folder(service, folder_name):
    # If folder is root folder, then return root:
    if folder_name == root_folder_name:
        root = service.files().get(fileId="root").execute()
        return root
    
    # Search for files with that name:
    results = service.files().list(q="name='"+folder_name+"'", fields="files(id, name, mimeType)").execute()
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
        
def copy_folder(service, folder, new_folder):
    print("Started copying folder", folder.get("name"))
    # Create a copy of the folder
    metadata = {
        "name": folder.get("name"),
        "mimeType": folder_mime_type,
        "parents": [new_folder.get("id")]
    }
    folder_copy = service.files().create(body=metadata, fields="id, name, mimeType").execute()
    
    # Get all of the files in this folder:
    results = service.files().list(q="'"+folder.get("id")+"' in parents", fields="files(id, name, mimeType)").execute()
    items = results.get("files", [])
    # Copy every file in this folder:
    for file in items:
        # Make a recursive call if this file is a folder:
        if file.get("mimeType") == folder_mime_type:
            copy_folder(service, file, folder_copy)
        # Otherwise, just make a normal copy by copying the file and putting it in the right folder:
        else:
            metadata = {
                "name": file.get("name"),
                "parents": [folder_copy.get("id")]
            }
            new_file = service.files().copy(body=metadata, fileId=file.get("id"), fields="id, name, mimeType").execute()
            print("Copied file", file.get("name"))
    print("Finished copying folder", folder.get("name"))

if __name__ == "__main__":
    main()