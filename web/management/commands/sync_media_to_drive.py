import os
import shutil
from django.core.management.base import BaseCommand
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from django.conf import settings


class Command(BaseCommand):
    help = "Uploads the media directory to Google Drive."

    def handle(self, *args, **kwargs):
        # Sprawdź, czy ustawienia są poprawnie skonfigurowane
        service_account_path = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_JSON_PATH", None)
        drive_folder_id = getattr(settings, "GOOGLE_DRIVE_FOLDER_ID", None)

        if not service_account_path or not drive_folder_id:
            self.stderr.write("GOOGLE_SERVICE_ACCOUNT_JSON_PATH and GOOGLE_DRIVE_FOLDER_ID must be set in settings.")
            return

        # Autoryzacja do Google API
        credentials = Credentials.from_service_account_file(service_account_path)
        service = build('drive', 'v3', credentials=credentials)

        # Usuń istniejący folder na Google Drive
        self._delete_existing_folder(service, drive_folder_id)

        # Utwórz nowy folder, jeśli nie istnieje
        self._ensure_folder_exists(service, drive_folder_id)

        # Prześlij katalog media
        media_path = os.path.join(settings.BASE_DIR, 'media')
        if os.path.exists(media_path):
            self._upload_directory(service, drive_folder_id, media_path)
            self.stdout.write("Media directory uploaded successfully.")
        else:
            self.stderr.write("Media directory does not exist.")

    def _delete_existing_folder(self, service, folder_id):
        """Delete all files and subfolders within the folder."""
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        for file in files:
            service.files().delete(fileId=file['id']).execute()
            self.stdout.write(f"Deleted: {file['name']} ({file['id']})")

    def _ensure_folder_exists(self, service, folder_id):
        """Ensure the target folder exists on Google Drive."""
        try:
            service.files().get(fileId=folder_id, fields='id').execute()
            self.stdout.write("Drive folder exists.")
        except Exception:
            self.stderr.write("Drive folder does not exist. Please create it manually.")

    def _upload_directory(self, service, parent_id, folder_path):
        """Upload a directory to Google Drive."""
        for root, _, files in os.walk(folder_path):
            folder_id = self._get_or_create_drive_folder(service, parent_id, os.path.relpath(root, folder_path))
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self._upload_file(service, folder_id, file_path)

    def _get_or_create_drive_folder(self, service, parent_id, folder_name):
        """Create a subfolder on Google Drive if it does not exist."""
        query = f"'{parent_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, fields="files(id)").execute()
        folders = results.get('files', [])

        if folders:
            return folders[0]['id']
        else:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = service.files().create(body=file_metadata, fields="id").execute()
            return folder['id']

    def _upload_file(self, service, folder_id, file_path):
        """Upload a single file to Google Drive."""
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        self.stdout.write(f"Uploaded: {file_path}")
