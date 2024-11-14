import os
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

class Command(BaseCommand):
    help = 'Synchronizuje katalog media z Google Drive, wysyłając tylko nowe lub zmienione pliki, z obsługą podkatalogów i ponownymi próbami przy błędach'

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

            self.stdout.write("Pobieranie istniejącej struktury folderu 'media' na Google Drive...")
            drive_media_folder_id = self.get_or_create_drive_folder(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)

            # Rekurencyjne mapowanie plików na Google Drive
            drive_files_map = self.map_drive_files(service, drive_media_folder_id)

            self.stdout.write("Synchronizacja lokalnego katalogu 'media' z Google Drive...")
            self.upload_folder(service, folder_path, drive_media_folder_id, drive_files_map)

            self.stdout.write(self.style.SUCCESS("Katalog 'media' został zsynchronizowany z Google Drive"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd podczas synchronizacji: {str(e)}'))

    def get_or_create_drive_folder(self, service, folder_name, parent_id=None):
        """Pobiera ID folderu na Google Drive lub tworzy go, jeśli nie istnieje."""
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

    def map_drive_files(self, service, folder_id):
        """Rekurencyjnie mapuje strukturę plików i folderów na Google Drive."""
        drive_files = {}

        def map_folder(drive_service, current_folder_id):
            query = f"'{current_folder_id}' in parents"
            results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name, size, mimeType)').execute()
            folder_contents = {}

            for file in results.get('files', []):
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    folder_contents[file['name']] = {
                        'id': file['id'],
                        'type': 'folder',
                        'children': map_folder(drive_service, file['id'])
                    }
                else:
                    folder_contents[file['name']] = {
                        'id': file['id'],
                        'type': 'file',
                        'size': int(file.get('size', 0))
                    }
            return folder_contents

        drive_files = map_folder(service, folder_id)
        return drive_files

    def upload_folder(self, service, folder_path, parent_id, drive_files_map):
        """Rekursywnie przesyła pliki i podfoldery z lokalnego folderu 'media'."""
        for root, dirs, files in os.walk(folder_path):
            relative_path = os.path.relpath(root, folder_path)
            folder_id = parent_id
            current_map = drive_files_map

            # Tworzymy podfoldery na Google Drive na podstawie struktury lokalnej
            if relative_path != ".":
                for folder_name in relative_path.split(os.sep):
                    if folder_name in current_map and current_map[folder_name]['type'] == 'folder':
                        folder_id = current_map[folder_name]['id']
                        current_map = current_map[folder_name]['children']
                    else:
                        folder_id = self.get_or_create_drive_folder(service, folder_name, folder_id)
                        current_map[folder_name] = {
                            'id': folder_id,
                            'type': 'folder',
                            'children': {}
                        }
                        current_map = current_map[folder_name]['children']

            # Przesyłanie plików
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_size = os.path.getsize(file_path)
                
                # Sprawdzanie, czy plik jest już na Google Drive i czy nie wymaga aktualizacji
                if file_name in current_map and current_map[file_name]['type'] == 'file':
                    drive_file = current_map[file_name]
                    if file_size == drive_file['size']:
                        self.stdout.write(f"Plik '{file_name}' jest już aktualny na Google Drive, pomijanie.")
                        continue
                    else:
                        # Nadpisanie zmienionego pliku
                        self.update_file_with_retry(service, file_path, drive_file['id'])
                else:
                    # Przesłanie nowego pliku
                    self.upload_file_with_retry(service, file_path, folder_id)
                    current_map[file_name] = {
                        'id': None,  # Do ustalenia, ale na razie pomijamy to po stronie Google Drive
                        'type': 'file',
                        'size': file_size
                    }

    def upload_file_with_retry(self, service, file_path, parent_id, retries=3):
        """Przesyła nowy plik na Google Drive, ponawiając próbę w razie błędu."""
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [parent_id]
        }
        media = MediaFileUpload(file_path, resumable=True)

        for attempt in range(retries):
            try:
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                self.stdout.write(self.style.SUCCESS(f"Przesłano nowy plik '{file_name}' na Google Drive"))
                return
            except HttpError as error:
                if error.resp.status == 302 and attempt < retries - 1:
                    self.stdout.write(self.style.WARNING(f"Przekierowanie podczas przesyłania '{file_name}', ponawiam próbę ({attempt + 1}/{retries})..."))
                    time.sleep(2)
                else:
                    self.stdout.write(self.style.ERROR(f"Nieudana próba przesłania '{file_name}': {error}"))
                    break

    def update_file_with_retry(self, service, file_path, file_id, retries=3):
        """Nadpisuje istniejący plik na Google Drive, ponawiając próbę w razie błędu."""
        file_name = os.path.basename(file_path)
        media = MediaFileUpload(file_path, resumable=True)

        for attempt in range(retries):
            try:
                service.files().update(fileId=file_id, media_body=media).execute()
                self.stdout.write(self.style.SUCCESS(f"Zaktualizowano plik '{file_name}' na Google Drive"))
                return
            except HttpError as error:
                if error.resp.status == 302 and attempt < retries - 1:
                    self.stdout.write(self.style.WARNING(f"Przekierowanie podczas aktualizacji '{file_name}', ponawiam próbę ({attempt + 1}/{retries})..."))
                    time.sleep(2)
                else:
                    self.stdout.write(self.style.ERROR(f"Nieudana próba aktualizacji '{file_name}': {error}"))
                    break
