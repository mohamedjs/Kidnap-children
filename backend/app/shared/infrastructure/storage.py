"""S3-compatible object storage (AWS S3, MinIO, SeaweedFS, R2, ...) via boto3.

Two clients: `internal` talks to S3_ENDPOINT (api/worker -> bucket); `signer` signs URLs
for S3_PUBLIC_ENDPOINT, the host the browser uses. Signing needs no network call.
The bucket stays private: every read is a short-lived presigned GET.
"""

from functools import lru_cache
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.shared.application.storage import ObjectInfo, ObjectStorage
from app.shared.infrastructure.config import Settings, get_settings


def _client(settings: Settings, endpoint: str) -> Any:
    return boto3.client(
        "s3",
        endpoint_url=endpoint or None,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key or None,
        aws_secret_access_key=settings.s3_secret_key or None,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if settings.s3_force_path_style else "auto"},
            retries={"max_attempts": 3},
        ),
    )


class S3Storage(ObjectStorage):
    def __init__(self, settings: Settings) -> None:
        self.bucket = settings.s3_bucket
        self.internal = _client(settings, settings.s3_endpoint)
        self.signer = _client(settings, settings.s3_public_endpoint or settings.s3_endpoint)

    def presign_put(self, key: str, content_type: str, ttl_seconds: int) -> str:
        url: str = self.signer.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=ttl_seconds,
            HttpMethod="PUT",
        )
        return url

    def presign_get(self, key: str, ttl_seconds: int, download_name: str | None = None) -> str:
        params: dict[str, str] = {"Bucket": self.bucket, "Key": key}
        if download_name:
            safe = "".join(c for c in download_name if c.isalnum() or c in "._- ")[:80] or "file"
            params["ResponseContentDisposition"] = f'attachment; filename="{safe}"'
        url: str = self.signer.generate_presigned_url("get_object", Params=params, ExpiresIn=ttl_seconds)
        return url

    def head(self, key: str) -> ObjectInfo | None:
        try:
            res = self.internal.head_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise
        return ObjectInfo(size=int(res["ContentLength"]), content_type=str(res.get("ContentType", "")))

    def delete(self, key: str) -> None:
        self.internal.delete_object(Bucket=self.bucket, Key=key)

    def read(self, key: str, max_bytes: int) -> bytes:
        res = self.internal.get_object(Bucket=self.bucket, Key=key, Range=f"bytes=0-{max_bytes - 1}")
        data: bytes = res["Body"].read()
        return data

    def ping(self) -> None:
        self.internal.head_bucket(Bucket=self.bucket)

    def ensure_bucket(self, allowed_origins: list[str]) -> None:
        try:
            self.internal.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.internal.create_bucket(Bucket=self.bucket)
        if allowed_origins:
            try:
                self.internal.put_bucket_cors(
                    Bucket=self.bucket,
                    CORSConfiguration={
                        "CORSRules": [
                            {
                                "AllowedOrigins": allowed_origins,
                                "AllowedMethods": ["GET", "PUT", "HEAD"],
                                "AllowedHeaders": ["*"],
                                "ExposeHeaders": ["ETag"],
                                "MaxAgeSeconds": 3600,
                            }
                        ]
                    },
                )
            except ClientError:
                # Some S3-compatible servers set CORS at server level instead (SeaweedFS: -s3.allowedOrigins).
                pass


@lru_cache
def get_storage() -> S3Storage:
    return S3Storage(get_settings())
