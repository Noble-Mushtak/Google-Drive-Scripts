from googleapiclient.discovery import build
from credentials import get_credentials
from view_doc import get_doc_text
from copy_folder import get_folder

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
# MIME type of Google Drive folder:
folder_mime_type = "application/vnd.google-apps.folder"
# MIME type of Google Docs:
doc_mime_type = "application/vnd.google-apps.document"

def main():
    # Get the user's credentials:
    creds = get_credentials(SCOPES)

    # Initialize the Drive and Docs APIs:
    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)

    # Ask user for the folder:
    print("This script counts the total number of words of all the Google Docs in a Google Drive folder.")
    folder_name = input("Enter the name of the folder: ")
    # Then, get the folder and count the number of words:
    folder = get_folder(drive_service, folder_name)
    count_words(drive_service, docs_service, folder)

def count_words(drive_service, docs_service, folder):
    print("Started counting words in", folder.get("name"), "folder")
    # This stores the total number of words in this folder:
    total = 0
    
    # Get all of the files in this folder:
    results = drive_service.files().list(q="'"+folder.get("id")+"' in parents", fields="files(id, name, mimeType)").execute()
    items = results.get("files", [])
    
    # Copy every file in this folder:
    for file in items:
        # Make a recursive call if this file is a folder:
        if file.get("mimeType") == folder_mime_type:
            total += count_words(drive_service, docs_service, file)
        # If this is a Google Doc, output the number of words:
        if file.get("mimeType") == doc_mime_type:
            word_count = len(get_doc_text(docs_service, file.get("id")).split())
            print(file.get("name"), "contains", word_count, "words")
            total += word_count
    # Finally, return the total:
    print(folder.get("name"), "folder contains", total, "words")
    return total

if __name__ == '__main__':
    main()