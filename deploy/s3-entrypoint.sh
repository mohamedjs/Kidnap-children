#!/bin/sh
# Writes the SeaweedFS S3 identity file from env (keys come from .env, never committed)
# and starts a single-node SeaweedFS with the S3 gateway on :8333.
set -eu
printf '{"identities":[{"name":"app","credentials":[{"accessKey":"%s","secretKey":"%s"}],"actions":["Admin","Read","Write","List","Tagging"]}]}' \
  "$S3_ACCESS_KEY" "$S3_SECRET_KEY" > /tmp/s3.json
exec weed server -dir=/data -ip.bind=0.0.0.0 -volume.max=0 -master.volumeSizeLimitMB=256 \
  -s3 -s3.port=8333 -s3.config=/tmp/s3.json -s3.allowedOrigins="$S3_ALLOWED_ORIGINS"
