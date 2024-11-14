import os
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class Command(BaseCommand):
    help = 'Synchronizes local media directory with Google Drive folder, preserving folder structure'

    def add_arguments(self, parser):
        parser.add_argument('folder_path', type=str, help='Path to the local media folder to be synchronized')

    def handle(self, *args, **kwargs):
        folder_path = kwargs['folder_path']
        
        if not os.path.isdir(folder_path):
            self.stdout.write(self.style.ERROR(f'Folder {folder_path} does not exist'))
            return

        try:
            # Uwierzytelnienie konta usługi
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            service = build('drive', 'v3', credentials=credentials)

            # Funkcja do wyszukiwania lub tworzenia folderów na Google Drive zgodnie ze strukturą lokalną
            def get_or_create_drive_folder(service, folder_name, parent_id=None):
                query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
                if parent_id:
                    query += f" and '{parent_id}' in parents"
                results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
                folders = results.get('files', [])

                if folders:
                    return folders[0]['id']
                else:
                    file_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [parent_id] if parent_id else []
                    }
                    folder = service.files().create(body=file_metadata, fields='id').execute()
                    return folder['id']

            # Pobieramy ID folderu głównego media na Google Drive
            drive_media_folder_id = get_or_create_drive_folder(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)

            # Zbieramy listę plików na Google Drive z zachowaniem struktury
            def get_drive_files_in_folder(drive_folder_id):
                results = service.files().list(q=f"'{drive_folder_id}' in parents", spaces='drive', fields='files(id, name, modifiedTime, mimeType)').execute()
                drive_files = {}
                for file in results.get('files', []):
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        drive_files[file['name']] = {
                            'id': file['id'],
                            'type': 'folder',
                            'children': get_drive_files_in_folder(file['id'])
                        }
                    else:
                        drive_files[file['name']] = {
                            'id': file['id'],
                            'type': 'file',
                            'modifiedTime': file['modifiedTime']
                        }
                return drive_files

            drive_files = get_drive_files_in_folder(drive_media_folder_id)

            # Przechodzimy przez lokalny folder i synchronizujemy pliki
            for root, _, files in os.walk(folder_path):
                relative_path = os.path.relpath(root, folder_path)
                current_drive_folder_id = drive_media_folder_id

                # Tworzymy strukturę folderów na Google Drive zgodnie ze strukturą lokalną
                if relative_path != ".":
                    for folder in relative_path.split(os.sep):
                        current_drive_folder_id = get_or_create_drive_folder(service, folder, current_drive_folder_id)

                for filename in files:
                    local_file_path = os.path.join(root, filename)
                    local_modified_time = os.path.getmtime(local_file_path)
                    
                    # Sprawdzenie, czy plik istnieje na Google Drive w odpowiednim folderze
                    if filename in drive_files.get(relative_path, {}):
                        drive_file = drive_files[relative_path][filename]
                        drive_modified_time = drive_file['modifiedTime']

                        # Porównujemy czas modyfikacji i przesyłamy plik, jeśli lokalny jest nowszy
                        if local_modified_time > int(drive_modified_time.timestamp()):
                            media = MediaFileUpload(local_file_path, resumable=True)
                            service.files().update(fileId=drive_file['id'], media_body=media).execute()
                            self.stdout.write(self.style.SUCCESS(f"Updated '{filename}' on Google Drive"))
                    else:
                        # Przesyłamy nowy plik
                        file_metadata = {
                            'name': filename,
                            'parents': [current_drive_folder_id]
                        }
                        media = MediaFileUpload(local_file_path, resumable=True)
                        uploaded_file = service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id'
                        ).execute()
                        self.stdout.write(self.style.SUCCESS(f"Uploaded new file '{filename}' to Google Drive"))

            # Usuwanie plików na Google Drive, które zostały usunięte lokalnie
            def delete_missing_files(drive_files, local_folder):
                for name, info in drive_files.items():
                    if info['type'] == 'file':
                        local_file_path = os.path.join(local_folder, name)
                        if not os.path.exists(local_file_path):
                            service.files().delete(fileId=info['id']).execute()
                            self.stdout.write(self.style.SUCCESS(f"Deleted '{name}' from Google Drive"))
                    elif info['type'] == 'folder':
                        local_subfolder = os.path.join(local_folder, name)
                        delete_missing_files(info['children'], local_subfolder)

            delete_missing_files(drive_files, folder_path)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during synchronization: {str(e)}'))
