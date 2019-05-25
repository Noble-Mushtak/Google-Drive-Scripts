from googleapiclient.discovery import build
from view_doc import get_doc_text
from utilities import *

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

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
    count_words(drive_service, folder, docs_service)

def begin_counting(drive_service, folder, docs_service):
    print("Started counting words in", folder.get("name"), "folder")
    # No additional arguments:
    return ()

def end_counting(drive_service, folder, num_words, *args):
    print(folder.get("name"), "folder contains", num_words, "words")
    # Do not change return value
    return num_words

@recurse_folder(begin_counting, end_counting)
def count_words(drive_service, file, docs_service):
    # Make a recursive call if this file is a folder:
    if file.get("mimeType") == folder_mime_type:
        return count_words(drive_service, file, docs_service)
    # If this is a Google Doc, return the number of words:
    if file.get("mimeType") == doc_mime_type:
        try:
            word_count = len(get_doc_text(docs_service, file.get("id")).split())
            print(file.get("name"), "contains", word_count, "words")
            return word_count
        except:
            print("Error counting", file.get("name"))
            
    # If nothing has been returned at this point, just return 0
    return 0

if __name__ == "__main__":
    main()