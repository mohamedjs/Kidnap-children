#!/usr/bin/env python3
"""Create .env.production from .env.production.example with random secrets.

    python3 scripts/gen-prod-env.py app.example.org files.example.org [--out .env.production]

Never overwrites an existing file and never prints secret values.
"""

import argparse
import pathlib
import secrets
import sys

root = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("app_domain")
ap.add_argument("files_domain")
ap.add_argument("--out", default=".env.production")
ap.add_argument("--http-only", action="store_true", help="local test: http:// addresses, no certificates")
ap.add_argument("--http-port", default="80")
ap.add_argument("--https-port", default="443")
a = ap.parse_args()

out = root / a.out
if out.exists():
    sys.exit(f"{out.name} already exists - leaving it alone")

scheme = "http" if a.http_only else "https"
port = "" if a.http_port == "80" or not a.http_only else f":{a.http_port}"
site = f"http://{a.app_domain}" if a.http_only else a.app_domain
files = f"http://{a.files_domain}" if a.http_only else a.files_domain
values = {
    "SITE_ADDRESS=app.example.org": f"SITE_ADDRESS={site}",
    "FILES_ADDRESS=files.example.org": f"FILES_ADDRESS={files}",
    "PUBLIC_WEB_URL=https://app.example.org": f"PUBLIC_WEB_URL={scheme}://{a.app_domain}{port}",
    "S3_PUBLIC_ENDPOINT=https://files.example.org": f"S3_PUBLIC_ENDPOINT={scheme}://{a.files_domain}{port}",
    "HTTP_PORT=80": f"HTTP_PORT={a.http_port}",
    "HTTPS_PORT=443": f"HTTPS_PORT={a.https_port}",
    "POSTGRES_PASSWORD=__generate__": f"POSTGRES_PASSWORD={secrets.token_urlsafe(24)}",
    "JWT_SECRET=__generate__": f"JWT_SECRET={secrets.token_urlsafe(48)}",
    "S3_ACCESS_KEY=__generate__": f"S3_ACCESS_KEY=kc{secrets.token_hex(10)}",
    "S3_SECRET_KEY=__generate__": f"S3_SECRET_KEY={secrets.token_urlsafe(36)}",
}
text = (root / ".env.production.example").read_text()
for old, new in values.items():
    text = text.replace(old, new, 1)
out.write_text(text)
out.chmod(0o600)
print(f"wrote {out.name} (secrets not printed)")
