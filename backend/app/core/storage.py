"""
S3-compatible object storage client for raw artifact uploads/downloads.
Works with MinIO (local dev) or AWS S3 / any S3-compatible service.
"""

from __future__ import annotations

import io
import logging
from typing import BinaryIO

import os
from pathlib import Path

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    boto3 = None
    BotoConfig = None
    ClientError = Exception
    BOTO3_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class ObjectStorage:
    """S3-compatible object storage for case artifacts with local fallback."""

    def __init__(self) -> None:
        self._client = None
        self._bucket = settings.S3_BUCKET_NAME
        self._local_storage_dir = Path(__file__).resolve().parent.parent.parent / "data_storage"
        self._local_storage_dir.mkdir(parents=True, exist_ok=True)

        if BOTO3_AVAILABLE:
            try:
                self._client = boto3.client(
                    "s3",
                    endpoint_url=settings.S3_ENDPOINT_URL,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION,
                    config=BotoConfig(signature_version="s3v4"),
                )
            except Exception as e:
                logger.warning("S3 client init failed, using local disk fallback: %s", e)

    def ensure_bucket(self) -> None:
        """Create the bucket if it doesn't exist."""
        if not self._client:
            return
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except Exception:
            try:
                logger.info("Creating S3 bucket: %s", self._bucket)
                self._client.create_bucket(Bucket=self._bucket)
            except Exception as e:
                logger.warning("Could not create S3 bucket: %s", e)

    def upload_artifact(
        self,
        case_id: str,
        filename: str,
        file_data: BinaryIO | bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a raw artifact and return the object key."""
        key = f"cases/{case_id}/{filename}"
        if isinstance(file_data, bytes):
            raw_bytes = file_data
        else:
            raw_bytes = file_data.read()

        if self._client:
            try:
                self._client.upload_fileobj(
                    io.BytesIO(raw_bytes),
                    self._bucket,
                    key,
                    ExtraArgs={"ContentType": content_type},
                )
                logger.info("Uploaded artifact to S3: %s", key)
                return key
            except Exception as e:
                logger.warning("S3 upload failed, using local disk: %s", e)

        local_path = self._local_storage_dir / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(raw_bytes)
        logger.info("Uploaded artifact to local disk: %s", key)
        return key

    def download_artifact(self, case_id: str, filename: str) -> bytes:
        """Download an artifact and return raw bytes."""
        key = f"cases/{case_id}/{filename}"
        return self.download_by_key(key)

    def download_by_key(self, key: str) -> bytes:
        """Download by direct object key."""
        if self._client:
            try:
                response = self._client.get_object(Bucket=self._bucket, Key=key)
                return response["Body"].read()
            except Exception as e:
                logger.warning("S3 download failed, checking local disk: %s", e)

        local_path = self._local_storage_dir / key
        if local_path.exists():
            return local_path.read_bytes()
        raise FileNotFoundError(f"Artifact {key} not found in storage")

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for downloading an artifact."""
        if self._client:
            try:
                return self._client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self._bucket, "Key": key},
                    ExpiresIn=expires_in,
                )
            except Exception:
                pass
        return f"/api/v1/cases/artifacts/download?key={key}"

    def upload_complaint_pdf(self, case_id: str, pdf_data: bytes) -> str:
        """Upload a generated complaint PDF."""
        key = f"complaints/{case_id}/complaint.pdf"
        if self._client:
            try:
                self._client.put_object(
                    Bucket=self._bucket,
                    Key=key,
                    Body=pdf_data,
                    ContentType="application/pdf",
                )
                logger.info("Uploaded complaint PDF to S3: %s", key)
                return key
            except Exception as e:
                logger.warning("S3 PDF upload failed, using local disk: %s", e)

        local_path = self._local_storage_dir / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(pdf_data)
        logger.info("Uploaded complaint PDF to local disk: %s", key)
        return key

    def delete_artifact(self, key: str) -> None:
        """Delete an object from storage."""
        if self._client:
            try:
                self._client.delete_object(Bucket=self._bucket, Key=key)
            except Exception:
                pass
        local_path = self._local_storage_dir / key
        if local_path.exists():
            local_path.unlink(missing_ok=True)



# Module-level singleton
object_storage = ObjectStorage()
