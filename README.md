# Google Drive Scripts
The following scripts are automations of some Google Drive tasks which may take a long time to do using the Google Drive GUI interface. To use any of these scripts, first, clone this GitHub repository and [follow the first two steps of this Quickstart guide](https://developers.google.com/drive/api/v3/quickstart/python). Make sure you download `credentials.json` into the working directory where you cloned the GitHub repository. Then, just use `python3` to run the script.

The below list explains the function of each script:

 * `copy_folder.py` recursively copies all of the files within a folder
 * `view_doc.py` outputs the text from a Google Doc
 * `count_words.py` recursively counts the total number of words of all of the Google Docs within a folder
 * After running one of the above scripts, `credentials.py` gets the OAuth2 client ID of the user who signed in and gave permission to the script