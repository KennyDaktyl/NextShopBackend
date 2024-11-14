import os
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

class Command(BaseCommand):
    help = 'Synchronizuje katalog media z Google Drive, wysyłając tylko nowe lub zmienione pliki bez dublowania i usuwania'

    def handle(self, *args, **kwargs):
        folder_path = settings.MEDIA_ROOT

        if not os.path.isdir(folder_path):
            self.stdout.write(self.style.ERROR(f'Folder {folder_path} nie istnieje'))
            return

        try:
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            service = build('drive', 'v3', credentials=credentials)

            # Pobierz ID głównego folderu 'media' na Google Drive, tworząc go, jeśli nie istnieje
            self.stdout.write("Sprawdzanie folderu 'media' na Google Drive...")
            drive_media_folder_id = self.get_or_create_drive_folder(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)

            self.stdout.write("Rozpoczynanie synchronizacji lokalnego katalogu 'media' z Google Drive...")
            self.sync_folder(service, folder_path, drive_media_folder_id)

            self.stdout.write(self.style.SUCCESS("Katalog 'media' został zsynchronizowany z Google Drive"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd podczas synchronizacji: {str(e)}'))

    def get_or_create_drive_folder(self, service, folder_name, parent_id=None):
        """Pobiera lub tworzy folder na Google Drive."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
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

    def sync_folder(self, service, local_folder_path, parent_id):
        """Synchronizuje lokalny folder z Google Drive bez dublowania plików."""
        for root, dirs, files in os.walk(local_folder_path):
            relative_path = os.path.relpath(root, local_folder_path)
            folder_id = parent_id

            if relative_path != ".":
                for folder_name in relative_path.split(os.sep):
                    folder_id = self.get_or_create_drive_folder(service, folder_name, folder_id)

            # Pobranie listy plików z obecnego folderu na Google Drive
            drive_files = self.get_drive_files_in_folder(service, folder_id)

            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_size = os.path.getsize(file_path)

                # Sprawdzenie, czy plik już istnieje i czy ma ten sam rozmiar
                if file_name in drive_files and drive_files[file_name]['size'] == file_size:
                    self.stdout.write(f"Plik '{file_name}' jest aktualny na Google Drive, pomijanie.")
                else:
                    # Jeśli plik jest nowy lub zmieniony, przesyłamy go
                    if file_name in drive_files:
                        self.update_file(service, file_path, drive_files[file_name]['id'])
                    else:
                        self.upload_file(service, file_path, folder_id)

    def get_drive_files_in_folder(self, service, folder_id):
        """Pobiera listę plików w folderze Google Drive, wraz z ich ID i rozmiarem."""
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name, size)').execute()
        
        drive_files = {}
        for file in results.get('files', []):
            drive_files[file['name']] = {
                'id': file['id'],
                'size': int(file.get('size', 0))
            }
        return drive_files

    def upload_file(self, service, file_path, parent_id):
        """Przesyła nowy plik na Google Drive."""
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [parent_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        self.stdout.write(self.style.SUCCESS(f"Przesłano nowy plik '{file_name}' na Google Drive"))

    def update_file(self, service, file_path, file_id):
        """Nadpisuje istniejący plik na Google Drive, jeśli został zmieniony lokalnie."""
        file_name = os.path.basename(file_path)
        media = MediaFileUpload(file_path, resumable=True)
        service.files().update(fileId=file_id, media_body=media).execute()
        self.stdout.write(self.style.SUCCESS(f"Zaktualizowano plik '{file_name}' na Google Drive"))
