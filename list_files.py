from drive_script import authenticate_drive

def list_drive_files():
    service = authenticate_drive()
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("No files found.")
    else:
        print("Files in Google Drive:")
        for file in files:
            print(f"{file['name']} ({file['id']})")

if __name__ == "__main__":
    list_drive_files()
