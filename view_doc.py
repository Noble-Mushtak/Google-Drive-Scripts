# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Recursively extracts the text from a Google Doc.
Source: https://developers.google.com/docs/api/samples/extract-text
"""

from googleapiclient.discovery import build
from utilities import *

# MIME type of Google Docs:
doc_mime_type = "application/vnd.google-apps.document"

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')


def read_strucutural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_strucutural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_strucutural_elements(toc.get('content'))
    return text

def get_doc_text(docs_service, document_id):
    """Uses the Docs API to print out the text of a document."""
    doc = docs_service.documents().get(documentId=document_id).execute()
    doc_content = doc.get('body').get('content')
    return read_strucutural_elements(doc_content)

def main():
    # Initialize the Docs and Drive services
    credentials = get_credentials(["https://www.googleapis.com/auth/drive"])
    drive_service = build("drive", "v3", credentials=credentials)
    docs_service = build("docs", "v1", credentials=credentials)
    
    # Ask user for document name:
    doc_name = input("Enter the name of the Google Docs you want to view: ")
    # Get the document and return if getting document fails:
    doc = get_document(drive_service, doc_name)
    if doc == None:
        return
    # Get the text content of the document:
    print(get_doc_text(docs_service, doc.get("id")))

def get_document(drive_service, doc_name):
    # Search for files with that name:
    results = drive_service.files().list(q="name='"+doc_name+"'", fields="files(id, name, mimeType)").execute()
    items = results.get("files", [])
    # Remove all non-docs from the list:
    for i in range(len(items)-1, -1, -1):
        folder = items[i]
        if folder.get("mimeType") != doc_mime_type:
            del items[i]
    
    # Return error if no documents found
    if len(items) == 0:
        print("No documents with that name found")
        return None
    # If there is only one document, return that document:
    if len(items) == 1:
        return items[0]
    
    # If there are multiple docs, ask the user to choose one:
    print("Multiple documents with that name found:")
    for i, doc in enumerate(items):
        print(str(i+1)+". "+doc.get("id")) 
    while True:
        # Ask the user to enter a number and return the doc corresponding to that number if possible.
        doc_index = input("Select the number corresponding to the correct document ID: ")
        try:
            doc_index = int(doc_index)
            if doc_index > 0 and doc_index <= len(items):
                return items[doc_index-1]
        except ValueError:
            pass
        print("No document ID corresponding to that number")

if __name__ == '__main__':
    main()
