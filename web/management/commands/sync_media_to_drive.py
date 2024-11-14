import os
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

class Command(BaseCommand):
    help = 'Usuwa zawartość katalogu media na Google Drive i przesyła nową zawartość z lokalnego katalogu media'

    MAX_RETRIES = 3  # Maksymalna liczba prób dla zapytań do Google Drive API
    RETRY_DELAY = 2  # Czas oczekiwania między ponownymi próbami (w sekundach)
    OPERATION_DELAY = 1  # Opóźnienie między operacjami przesyłania plików (w sekundach)

    def handle(self, *args, **kwargs):
        folder_path = settings.MEDIA_ROOT
        i = 0
        if not os.path.isdir(folder_path):
            self.stdout.write(self.style.ERROR(f'Folder {folder_path} nie istnieje'))
            return

        try:
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            service = build('drive', 'v3', credentials=credentials)

            # Usuń cały folder 'media' na Google Drive
            self.stdout.write("Usuwanie folderu 'media' na Google Drive...")
            drive_media_folder_id = self.get_or_create_drive_folder(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)
            self.delete_drive_folder(service, drive_media_folder_id)

            # Przesyłanie całego lokalnego katalogu 'media' na Google Drive
            self.stdout.write("Przesyłanie lokalnego katalogu 'media' na Google Drive...")
            self.upload_folder(service, folder_path, drive_media_folder_id, i)

            self.stdout.write(self.style.SUCCESS("Katalog 'media' został zaktualizowany na Google Drive"))

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

    def delete_drive_folder(self, service, folder_id):
        """Usuwa cały folder na Google Drive."""
        try:
            service.files().delete(fileId=folder_id).execute()
            self.stdout.write(self.style.SUCCESS(f"Usunięto folder 'media' na Google Drive"))
        except HttpError as error:
            if error.resp.status == 404:
                self.stdout.write(self.style.WARNING("Folder 'media' już został usunięty"))
            else:
                self.stdout.write(self.style.ERROR(f"Błąd podczas usuwania folderu: {error}"))

    def upload_folder(self, service, folder_path, parent_id, i=0):
        """Rekursywnie przesyła lokalny folder na Google Drive."""
        for root, dirs, files in os.walk(folder_path):
            relative_path = os.path.relpath(root, folder_path)
            folder_id = parent_id

            # Tworzymy strukturę podfolderów na Google Drive zgodnie ze strukturą lokalną
            if relative_path != ".":
                for folder_name in relative_path.split(os.sep):
                    folder_id = self.get_or_create_subfolder(service, folder_name, folder_id)

            # Przesyłanie plików w aktualnym folderze
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.upload_file(service, file_path, folder_id, i)
                i += 1
            # Dodanie opóźnienia po każdym katalogu
            time.sleep(self.OPERATION_DELAY)

    def get_or_create_subfolder(self, service, folder_name, parent_id):
        """Tworzy lub pobiera istniejący podfolder na Google Drive."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
        results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        else:
            return self.create_drive_folder(service, folder_name, parent_id)

    def create_drive_folder(self, service, folder_name, parent_id=None):
        """Tworzy nowy folder na Google Drive."""
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else []
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder['id']

    def upload_file(self, service, file_path, parent_id, i):
        """Przesyła pojedynczy plik do określonego folderu na Google Drive z obsługą ponawiania prób."""
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [parent_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        for attempt in range(self.MAX_RETRIES):
            try:
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                self.stdout.write(self.style.SUCCESS(f"Przesłano '{file_name}' na Google Drive numer iteracji: {i}"))
                time.sleep(self.OPERATION_DELAY)  # Opóźnienie między przesyłaniem plików
                return
            except HttpError as error:
                if error.resp.status in [500, 502, 503, 504, 429]:
                    self.stdout.write(self.style.WARNING(f"Błąd API {error.resp.status}. Ponawiam próbę dla '{file_name}'..."))
                    time.sleep(self.RETRY_DELAY)
                elif error.resp.status == 302:
                    self.stdout.write(self.style.WARNING(f"Błąd przekierowania dla '{file_name}'. Ponawiam próbę..."))
                    time.sleep(self.RETRY_DELAY)
                else:
                    self.stdout.write(self.style.ERROR(f"Nieudana próba przesłania '{file_name}': {error}"))
                    break
