"""Create the private bucket (and CORS where the server supports it). Idempotent."""

from app.shared.infrastructure.config import get_settings
from app.shared.infrastructure.storage import get_storage


def main() -> None:
    s = get_settings()
    origins = [o.strip() for o in (s.s3_allowed_origins or s.cors_origins).split(",") if o.strip()]
    get_storage().ensure_bucket(origins)
    print(f"bucket '{s.s3_bucket}' ready")


if __name__ == "__main__":
    main()
