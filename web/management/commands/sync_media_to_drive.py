import os
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class Command(BaseCommand):
    help = 'Optimized synchronization of the local media directory with Google Drive folder, preserving folder structure'

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

            # Tworzenie rekurencyjnego odwzorowania struktury folderu Google Drive
            def map_drive_structure(drive_folder_id):
                results = service.files().list(
                    q=f"'{drive_folder_id}' in parents",
                    spaces='drive',
                    fields='files(id, name, mimeType, modifiedTime)').execute()
                
                drive_structure = {}
                for file in results.get('files', []):
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        drive_structure[file['name']] = {
                            'id': file['id'],
                            'type': 'folder',
                            'children': map_drive_structure(file['id'])
                        }
                    else:
                        drive_structure[file['name']] = {
                            'id': file['id'],
                            'type': 'file',
                            'modifiedTime': file['modifiedTime']
                        }
                return drive_structure

            # Pobieramy strukturę folderu "media" na Google Drive
            drive_media_folder_id = self.get_or_create_drive_folder(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)
            drive_files = map_drive_structure(drive_media_folder_id)

            # Mapa plików lokalnych do porównania
            local_files = {}
            for root, _, files in os.walk(folder_path):
                relative_path = os.path.relpath(root, folder_path)
                local_files[relative_path] = {
                    f: os.path.getmtime(os.path.join(root, f)) for f in files
                }

            # Synchronizacja
            self.sync_folders(service, drive_files, local_files, drive_media_folder_id, folder_path)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during synchronization: {str(e)}'))

    def sync_folders(self, service, drive_files, local_files, parent_id, base_folder):
        # Usuwanie plików z Google Drive, które zostały usunięte lokalnie
        for drive_filename, drive_file in drive_files.items():
            if drive_file['type'] == 'file':
                if drive_filename not in local_files.get("", {}):
                    service.files().delete(fileId=drive_file['id']).execute()
                    self.stdout.write(self.style.SUCCESS(f"Deleted '{drive_filename}' from Google Drive"))
            elif drive_file['type'] == 'folder' and drive_filename not in local_files:
                service.files().delete(fileId=drive_file['id']).execute()
                self.stdout.write(self.style.SUCCESS(f"Deleted folder '{drive_filename}' from Google Drive"))

        # Dodawanie i aktualizowanie plików na Google Drive
        for relative_path, files in local_files.items():
            current_drive_folder_id = parent_id
            if relative_path != ".":
                for folder in relative_path.split(os.sep):
                    current_drive_folder_id = self.get_or_create_drive_folder(service, folder, current_drive_folder_id)

            for filename, local_modified_time in files.items():
                local_file_path = os.path.join(base_folder, relative_path, filename)
                if filename in drive_files.get(relative_path, {}):
                    drive_file = drive_files[relative_path][filename]
                    drive_modified_time = drive_file['modifiedTime']
                    if local_modified_time > int(drive_modified_time.timestamp()):
                        media = MediaFileUpload(local_file_path, resumable=True)
                        service.files().update(fileId=drive_file['id'], media_body=media).execute()
                        self.stdout.write(self.style.SUCCESS(f"Updated '{filename}' on Google Drive"))
                else:
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

    def get_or_create_drive_folder(self, service, folder_name, parent_id=None):
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
