from googleapiclient.discovery import build
from utilities import *

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    # Get the user's credentials:
    creds = get_credentials(SCOPES)

    # Initialize the Drive API:
    drive_service = build("drive", "v3", credentials=creds)
    
    # Ask user for the folder:
    print("This script counts the total number of words of all the Google Docs in a Google Drive folder.")
    folder_name = input("Enter the name of the folder: ")
    # Then, get the folder and calculate the size:
    folder = get_folder(drive_service, folder_name)
    print(calc_size(drive_service, folder, 0)[1])

def begin_calculation(drive_service, folder, level):
    print("Started calculating size of", folder.get("name"), "folder")
    # No additional arguments:
    return ()

def add_num_and_string(tpl1, tpl2):
    return (tpl1[0]+tpl2[0], tpl1[1]+tpl2[1])

def end_calculation(drive_service, folder, tpl, level):
    print("Finished calculating size of", folder.get("name"), "folder")
    
    num_bytes = tpl[0]
    # Print string describing folder
    str_ = ""
    if num_bytes > 0:
        if level > 0:
            str_ += " >"*level+" "
        str_ += folder.get("name")+" folder contains "+str(num_bytes)+" bytes\n"
    # Append str to output string:
    return (num_bytes, str_+tpl[1])

@recurse_folder(begin_calculation, end_calculation, (0, ""), add_num_and_string)
def calc_size(drive_service, file, level):
    # Make a recursive call if this file is a folder:
    if file.get("mimeType") == folder_mime_type:
        return calc_size(drive_service, file, level+1)
    # Otherwise, just return the size:
    byte_size = int(file.get("size", 0))
    str_ = ""
    if byte_size > 0:
        str_ += " >"*(level+1)+" "
        str_ += file.get("name")+" contains "+str(byte_size)+" bytes\n"
    return (byte_size, str_)

if __name__ == "__main__":
    main()