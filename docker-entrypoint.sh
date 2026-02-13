#!/bin/bash
set -ue
shopt -s nullglob

export TZ=${TZ:-Asia/Tokyo}

if [ -z "${SAKURA_ARTIFACT_DIR:-}" ]; then
      	echo "Environment variable SAKURA_ARTIFACT_DIR is not set" >&2
      	exit 1
fi

if [ -z "${SAKURA_TASK_ID:-}" ]; then
      	echo "Environment variable SAKURA_TASK_ID is not set" >&2
	exit 1
fi

if [ -z "${TASKS:-}" ]; then
      	echo "Environment variable TASKS is not set" >&2
	exit 1
fi

cd /Real-ESRGAN

python3 runner.py \
  --output="${SAKURA_ARTIFACT_DIR}" \
  --inputbucket="${INPUT_BUCKET}" \
  --outputbucket="${OUTPUT_BUCKET}" \
  --tasks="${TASKS}" \
  --s3-endpoint="${S3_ENDPOINT:-}" \
  --s3-secret="${S3_SECRET:-}" \
  --s3-token="${S3_TOKEN:-}"
