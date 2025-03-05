from drive_script import authenticate_drive

def download_file(file_id, save_path):
    """Download binary files and export Google Docs, Sheets, or Slides files."""
    service = authenticate_drive()
    
    # Get file metadata to check file type
    file_metadata = service.files().get(fileId=file_id).execute()
    mime_type = file_metadata.get("mimeType", "")
    
    # If it's a Google Docs/Sheets/Slides file, export it
    if "application/vnd.google-apps" in mime_type:
        export_mime_type = {
            "application/vnd.google-apps.document": "application/pdf",  # Google Docs → PDF
            "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Google Sheets → Excel
            "application/vnd.google-apps.presentation": "application/pdf",  # Google Slides → PDF
        }
        
        if mime_type in export_mime_type:
            request = service.files().export_media(fileId=file_id, mimeType=export_mime_type[mime_type])
            print(f"Exporting {file_metadata['name']} as {export_mime_type[mime_type]}")
        else:
            print("This Google file type cannot be exported.")
            return
    else:
        request = service.files().get_media(fileId=file_id)  # Regular download

    # Save the file
    with open(save_path, "wb") as f:
        f.write(request.execute())

    print(f"File downloaded to {save_path}")

if __name__ == "__main__":
    file_id = input("Enter the Google Drive File ID: ")
    save_path = input("Enter the local path to save the file: ")
    download_file(file_id, save_path)
