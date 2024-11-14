import os
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

class Command(BaseCommand):
    help = 'Zastępuje katalog media na Google Drive wersją lokalną, używając MEDIA_ROOT'

    def handle(self, *args, **kwargs):
        # Pobierz lokalizację katalogu 'media' z MEDIA_ROOT
        folder_path = settings.MEDIA_ROOT
        
        if not os.path.isdir(folder_path):
            self.stdout.write(self.style.ERROR(f'Folder {folder_path} nie istnieje'))
            return

        try:
            # Autoryzacja do Google Drive
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            service = build('drive', 'v3', credentials=credentials)

            # Usuń istniejący folder 'media' na Google Drive, jeśli istnieje
            self.stdout.write("Usuwam istniejący folder 'media' na Google Drive...")
            media_folder_id = self.get_drive_folder_id(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)
            if media_folder_id:
                service.files().delete(fileId=media_folder_id).execute()
                self.stdout.write(self.style.SUCCESS("Usunięto istniejący folder 'media' na Google Drive"))

            # Tworzenie nowego folderu 'media' i przesyłanie całości zawartości
            self.stdout.write("Tworzenie nowego folderu 'media' na Google Drive...")
            drive_media_folder_id = self.create_drive_folder(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)
            
            self.stdout.write("Przesyłanie lokalnego katalogu media na Google Drive...")
            self.upload_folder(service, folder_path, drive_media_folder_id)

            self.stdout.write(self.style.SUCCESS("Folder media został pomyślnie zastąpiony na Google Drive"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd podczas przesyłania: {str(e)}'))

    def get_drive_folder_id(self, service, folder_name, parent_id):
        """Pobiera ID folderu na Google Drive, jeśli istnieje."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
        results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
        folders = results.get('files', [])
        return folders[0]['id'] if folders else None

    def create_drive_folder(self, service, folder_name, parent_id=None):
        """Tworzy folder na Google Drive."""
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else []
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder['id']

    def upload_folder(self, service, folder_path, parent_id):
        """Rekursywnie przesyła wszystkie pliki i podfoldery z lokalnego folderu 'media'."""
        for root, dirs, files in os.walk(folder_path):
            relative_path = os.path.relpath(root, folder_path)
            folder_id = parent_id

            # Tworzymy podfoldery na Google Drive na podstawie struktury lokalnej
            if relative_path != ".":
                folder_id = self.create_drive_folder(service, relative_path, folder_id)

            # Przesyłanie plików w aktualnym folderze
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.upload_file(service, file_path, folder_id)

    def upload_file(self, service, file_path, parent_id):
        """Przesyła pojedynczy plik do określonego folderu na Google Drive."""
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [parent_id]
        }
        media = MediaFileUpload(file_path, chunksize=256*1024, resumable=True)
        upload = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        )

        # Przesyłanie z potwierdzeniem ukończenia
        response = None
        while response is None:
            status, response = upload.next_chunk()
            if status:
                self.stdout.write(f"Przesyłanie {file_name}: {int(status.progress() * 100)}% zakończone")
        self.stdout.write(self.style.SUCCESS(f"Przesłano '{file_name}' na Google Drive"))
