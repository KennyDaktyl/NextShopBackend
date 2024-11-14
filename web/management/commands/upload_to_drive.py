import os
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

class Command(BaseCommand):
    help = 'Uploads a database backup to Google Drive, replacing the old backup if it exists'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the database backup file to be uploaded')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File {file_path} does not exist'))
            return

        try:
            # Uwierzytelnienie konta usługi
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            service = build('drive', 'v3', credentials=credentials)

            # Nazwa pliku na Google Drive (możemy ustawić ją na stałą nazwę np. "database_backup.sql")
            drive_file_name = "serwiswrybnej_backup.sql"

            # Wyszukaj istniejący plik na Google Drive
            query = f"name='{drive_file_name}' and '{settings.GOOGLE_DRIVE_FOLDER_ID}' in parents"
            results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            files = results.get('files', [])

            # Usuń istniejący plik, jeśli został znaleziony
            if files:
                file_id = files[0]['id']
                service.files().delete(fileId=file_id).execute()
                self.stdout.write(self.style.SUCCESS(f"Existing file '{drive_file_name}' deleted"))

            # Przesyłanie nowego pliku na Google Drive
            file_metadata = {
                'name': drive_file_name,
                'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]  # Folder docelowy na Drive
            }
            media = MediaFileUpload(file_path, resumable=True)
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            self.stdout.write(self.style.SUCCESS(f"New backup '{drive_file_name}' uploaded with ID: {uploaded_file.get('id')}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error uploading file: {str(e)}'))
