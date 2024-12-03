import os
import shutil
import time

from django.core.management.base import BaseCommand
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from django.conf import settings


class Command(BaseCommand):
    help = "Compress the media directory and upload it as a single ZIP file to Google Drive."

    def handle(self, *args, **kwargs):
        # Sprawdzanie konfiguracji
        service_account_path = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_JSON_PATH", None)
        drive_folder_id = getattr(settings, "GOOGLE_DRIVE_FOLDER_ID", None)

        if not service_account_path or not drive_folder_id:
            self.stderr.write("GOOGLE_SERVICE_ACCOUNT_JSON_PATH and GOOGLE_DRIVE_FOLDER_ID must be set in settings.")
            return

        # Autoryzacja do Google API
        credentials = Credentials.from_service_account_file(service_account_path)
        service = build('drive', 'v3', credentials=credentials)

        # Ścieżki plików
        media_dir = os.path.join(settings.BASE_DIR, 'media')
        zip_file_path = os.path.join(settings.BASE_DIR, 'media.zip')

        # Spakowanie katalogu media
        if os.path.exists(media_dir):
            self._compress_directory(media_dir, zip_file_path)
            self.stdout.write(f"Media directory compressed to {zip_file_path}")
        else:
            self.stderr.write("Media directory does not exist.")
            return

        # Usuwanie istniejącego pliku na Google Drive (jeśli istnieje)
        self._delete_existing_file(service, drive_folder_id, "media.zip")

        # Wysyłanie pliku na Google Drive
        self._upload_file(service, drive_folder_id, zip_file_path)
        self.stdout.write("Media.zip uploaded successfully.")

        # Usuwanie lokalnego pliku ZIP
        os.remove(zip_file_path)
        self.stdout.write("Local zip file removed.")

    def _compress_directory(self, source_dir, output_zip):
        """Tworzy plik ZIP z katalogu."""
        shutil.make_archive(output_zip.replace('.zip', ''), 'zip', source_dir)

    def _delete_existing_file(self, service, folder_id, file_name):
        """Usuwa plik z Google Drive, jeśli istnieje."""
        query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])

        for file in files:
            service.files().delete(fileId=file['id']).execute()
            self.stdout.write(f"Deleted: {file_name} ({file['id']})")

    def _upload_file(self, service, folder_id, file_path):
        """Wysyła plik na Google Drive z informacją o postępie."""
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, mimetype='application/zip', resumable=True)

        # Inicjalizacja uploadu
        request = service.files().create(body=file_metadata, media_body=media, fields="id")
        response = None
        total_size = os.path.getsize(file_path)
        uploaded_size = 0

        self.stdout.write(f"Starting upload of {os.path.basename(file_path)} ({total_size / (1024 * 1024):.2f} MB)")

        while response is None:
            status, response = request.next_chunk()
            if status:
                uploaded_size = status.resumable_progress
                progress = (uploaded_size / total_size) * 100
                self.stdout.write(f"Upload progress: {progress:.2f}% ({uploaded_size / (1024 * 1024):.2f} MB uploaded)")
                time.sleep(0.5)  # Opcjonalnie, aby uniknąć zbyt częstego logowania

        self.stdout.write(f"Upload completed. File ID: {response.get('id')}")
