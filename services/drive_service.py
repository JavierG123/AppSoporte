import io
import logging
import zipfile
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

LOGGER = logging.getLogger(__name__)


def authenticate_user(root_path: Path, show_auth_message: Callable[[], None]) -> Credentials:
    """Authenticate user against Google Drive API and return credentials."""
    scopes = ["https://www.googleapis.com/auth/drive"]
    credentials_path = root_path / "data" / "credentials.json"
    token_path = root_path / "token.json"

    creds: Optional[Credentials] = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            show_auth_message()
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), scopes)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds


def find_files(
    root_path: Path,
    config: Dict[str, str],
    show_auth_message: Callable[[], None],
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """List installer and tool files in configured Google Drive folders."""
    programs_folder_id = config["programsFolder"]
    genesys_tools_folder_id = config["genesysToolsFolder"]

    creds = authenticate_user(root_path, show_auth_message)
    drive_service = build("drive", "v3", credentials=creds, static_discovery=False)

    query_programs = f"'{programs_folder_id}' in parents and trashed = false"
    query_tools = f"'{genesys_tools_folder_id}' in parents and trashed = false"

    results_programs = drive_service.files().list(
        q=query_programs,
        fields="nextPageToken, files(id, name)",
    ).execute()
    results_tools = drive_service.files().list(
        q=query_tools,
        fields="nextPageToken, files(id, name)",
    ).execute()

    installers = [(file.get("id"), file.get("name")) for file in results_programs.get("files", [])]
    tools = [(file.get("id"), file.get("name")) for file in results_tools.get("files", [])]
    return installers, tools


def download_from_gdrive(
    root_path: Path,
    file_id: str,
    show_auth_message: Callable[[], None],
    tools_directory: Optional[Path] = None,
) -> bytes:
    """Download a file from Google Drive and extract zip files in tools directory."""
    downloaded_buffer = io.BytesIO()

    try:
        creds = authenticate_user(root_path, show_auth_message)
        service = build("drive", "v3", credentials=creds, static_discovery=False)
        request = service.files().get_media(fileId=file_id)
        file_data = service.files().get(fileId=file_id).execute()
        file_name = file_data.get("name")

        downloader = MediaIoBaseDownload(downloaded_buffer, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            LOGGER.info("Download %s%%", int(status.progress() * 100))

        downloaded_buffer.seek(0)
        local_path = Path.cwd() / file_name
        with open(local_path, "wb") as file_obj:
            file_obj.write(downloaded_buffer.read())

        if file_name.endswith(".zip") and tools_directory:
            with zipfile.ZipFile(local_path, "r") as zip_file:
                zip_file.extractall(tools_directory)
    except HttpError:
        LOGGER.exception("An error occurred while downloading from Google Drive")

    return downloaded_buffer.getvalue()
