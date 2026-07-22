import json
import os
import re
import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status

try:
    import magic
except ImportError:  # pragma: no cover - dependency is expected in runtime requirements
    magic = None


ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".pdf", ".docx", ".json"}
MAX_FILE_SIZE = 100 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024

PDF_SIGNATURE = b"%PDF"
ZIP_SIGNATURE = b"PK\x03\x04"
XLS_SIGNATURE = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"

TEXT_MIME_PREFIXES = ("text/",)
CSV_MIME_TYPES = {
    "application/csv",
    "application/vnd.ms-excel",
    "application/octet-stream",
    "text/plain",
}
JSON_MIME_TYPES = {
    "application/json",
    "text/json",
    "text/plain",
    "application/octet-stream",
}
PDF_MIME_TYPES = {"application/pdf"}
XLSX_MIME_TYPES = {
    "application/zip",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
DOCX_MIME_TYPES = {
    "application/zip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
XLS_MIME_TYPES = {
    "application/vnd.ms-excel",
    "application/octet-stream",
    "application/x-ole-storage",
    "application/CDFV2",
}

UPLOADS_DIR = Path(__file__).resolve().parents[3] / "uploads"


def sanitize_filename(filename: str) -> str:
    """
    Removes dangerous path and control characters from a user-supplied filename.
    """
    cleaned = (filename or "report").replace("\x00", "")
    cleaned = cleaned.replace("\\", "/").split("/")[-1]
    cleaned = cleaned.replace("..", "")
    cleaned = re.sub(r"[\r\n\t]", " ", cleaned)
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", cleaned).strip(" .")
    return cleaned or "report"


def get_extension(filename: str) -> str:
    """
    Returns a lowercase extension and rejects unsupported file types.
    """
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )
    return extension


def build_stored_filename(original_name: str) -> str:
    """
    Generates a unique on-disk filename using a UUID prefix.
    """
    return f"{uuid.uuid4()}-{original_name}"


def _detect_mime(sample: bytes) -> Optional[str]:
    if not sample or magic is None:
        return None
    return magic.from_buffer(sample, mime=True)


def _looks_like_csv(sample: bytes, mime_type: Optional[str]) -> bool:
    if b"\x00" in sample:
        return False

    if mime_type and (mime_type.startswith(TEXT_MIME_PREFIXES) or mime_type in CSV_MIME_TYPES):
        return True

    try:
        decoded = sample.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            decoded = sample.decode("latin-1")
        except UnicodeDecodeError:
            return False

    return any(separator in decoded for separator in [",", ";", "\t"]) and "\n" in decoded


def _looks_like_json(sample: bytes, mime_type: Optional[str]) -> bool:
    if b"\x00" in sample:
        return False

    if mime_type and (mime_type.startswith(TEXT_MIME_PREFIXES) or mime_type in JSON_MIME_TYPES):
        try:
            decoded = sample.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                decoded = sample.decode("latin-1")
            except UnicodeDecodeError:
                return False
    else:
        try:
            decoded = sample.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                decoded = sample.decode("latin-1")
            except UnicodeDecodeError:
                return False

    stripped = decoded.strip()
    if not stripped or stripped[0] not in "[{":
        return False

    try:
        json.loads(stripped)
        return True
    except json.JSONDecodeError:
        return False


def validate_file_signature(extension: str, sample: bytes) -> None:
    """
    Validates the uploaded file's leading bytes and MIME hints against the supported types.
    """
    mime_type = _detect_mime(sample)

    is_valid = False
    if extension == ".pdf":
        is_valid = sample.startswith(PDF_SIGNATURE) and (mime_type in PDF_MIME_TYPES or mime_type is None)
    elif extension in {".xlsx", ".docx"}:
        accepted_mimes = XLSX_MIME_TYPES if extension == ".xlsx" else DOCX_MIME_TYPES
        is_valid = sample.startswith(ZIP_SIGNATURE) and (mime_type in accepted_mimes or mime_type is None)
    elif extension == ".xls":
        is_valid = sample.startswith(XLS_SIGNATURE) and (mime_type in XLS_MIME_TYPES or mime_type is None)
    elif extension == ".csv":
        is_valid = _looks_like_csv(sample, mime_type)
    elif extension == ".json":
        is_valid = _looks_like_json(sample, mime_type)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File appears to be empty or corrupted",
        )


async def save_upload_file(upload_file: UploadFile) -> dict:
    """
    Streams an uploaded file to disk while enforcing size and signature validation.
    """
    sanitized_name = sanitize_filename(upload_file.filename or "report")
    extension = get_extension(sanitized_name)
    stored_name = build_stored_filename(sanitized_name)

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    final_path = UPLOADS_DIR / stored_name
    temp_path = final_path.with_suffix(f"{final_path.suffix}.uploading")

    total_size = 0
    sample = bytearray()

    try:
        with temp_path.open("wb") as output_file:
            while True:
                chunk = await upload_file.read(CHUNK_SIZE)
                if not chunk:
                    break

                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds 100MB limit",
                    )

                if len(sample) < 8192:
                    remaining = 8192 - len(sample)
                    sample.extend(chunk[:remaining])

                output_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File appears to be empty or corrupted",
            )

        validate_file_signature(extension, bytes(sample))
        os.replace(temp_path, final_path)

        return {
            "original_name": sanitized_name,
            "stored_name": stored_name,
            "file_type": extension.lstrip("."),
            "file_size": total_size,
            "file_path": final_path,
        }
    except HTTPException:
        if temp_path.exists():
            temp_path.unlink()
        raise
    except Exception as exc:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store uploaded file",
        ) from exc
    finally:
        await upload_file.close()


def delete_file(stored_name: str) -> None:
    """
    Removes a previously stored file from disk if it still exists.
    """
    file_path = UPLOADS_DIR / stored_name
    if file_path.exists():
        file_path.unlink()
