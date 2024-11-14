import os
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

class Command(BaseCommand):
    help = 'Replaces entire media directory on Google Drive with local version using MEDIA_ROOT'

    def handle(self, *args, **kwargs):
        # Pobierz lokalizację katalogu 'media' z MEDIA_ROOT
        folder_path = settings.MEDIA_ROOT
        
        if not os.path.isdir(folder_path):
            self.stdout.write(self.style.ERROR(f'Folder {folder_path} does not exist'))
            return

        try:
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            service = build('drive', 'v3', credentials=credentials)

            # Usuń istniejący folder 'media' na Google Drive, jeśli istnieje
            self.stdout.write("Deleting existing 'media' folder on Google Drive...")
            self.delete_drive_folder(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)

            # Twórz nowy folder 'media' i przesyłaj całą strukturę
            self.stdout.write("Creating new 'media' folder on Google Drive...")
            drive_media_folder_id = self.create_drive_folder(service, 'media', settings.GOOGLE_DRIVE_FOLDER_ID)
            
            self.stdout.write("Uploading local media folder to Google Drive...")
            self.upload_folder(service, folder_path, drive_media_folder_id)

            self.stdout.write(self.style.SUCCESS("Media folder successfully replaced on Google Drive"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during upload: {str(e)}'))

    def delete_drive_folder(self, service, folder_name, parent_id):
        """Usuwa folder na Google Drive według nazwy, jeśli istnieje."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
        results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
        
        for file in results.get('files', []):
            try:
                service.files().delete(fileId=file['id']).execute()
                self.stdout.write(self.style.SUCCESS(f"Deleted folder '{folder_name}' on Google Drive"))
            except HttpError as error:
                if error.resp.status == 404:
                    self.stdout.write(self.style.WARNING(f"Folder '{folder_name}' already deleted"))
                else:
                    raise

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
        """Rekursywnie przesyła lokalny folder na Google Drive."""
        for root, dirs, files in os.walk(folder_path):
            relative_path = os.path.relpath(root, folder_path)
            folder_id = parent_id

            if relative_path != ".":
                # Tworzymy podfoldery na Google Drive
                for folder_name in relative_path.split(os.sep):
                    folder_id = self.get_or_create_subfolder(service, folder_name, folder_id)

            # Przesyłanie plików w aktualnym folderze
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.upload_file(service, file_path, folder_id)

    def get_or_create_subfolder(self, service, folder_name, parent_id):
        """Tworzy lub pobiera istniejący podfolder na Google Drive."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
        results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        else:
            return self.create_drive_folder(service, folder_name, parent_id)

    def upload_file(self, service, file_path, parent_id):
        """Przesyła pojedynczy plik do określonego folderu na Google Drive."""
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [parent_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        self.stdout.write(self.style.SUCCESS(f"Uploaded '{file_name}' to Google Drive"))
