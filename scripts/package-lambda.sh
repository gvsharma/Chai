#!/usr/bin/env bash
# Package a CHAI agent for AWS Lambda (Python 3.12).
set -euo pipefail

AGENT="${1:-gmail}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$(mktemp -d)"
OUTPUT_ZIP="${OUTPUT_ZIP:-${ROOT}/dist/lambda-${AGENT}.zip}"
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"

cleanup() {
  rm -rf "$BUILD_DIR"
}
trap cleanup EXIT

mkdir -p "$(dirname "$OUTPUT_ZIP")"

case "$AGENT" in
  gmail)
    mkdir -p "$BUILD_DIR/agents"
    cp -R "$ROOT/agents/gmail" "$BUILD_DIR/agents/"
    cp -R "$ROOT/shared" "$BUILD_DIR/"
  ;;
  *)
    echo "Unsupported agent: $AGENT" >&2
    echo "Supported agents: gmail" >&2
    exit 1
  ;;
esac

python${PYTHON_VERSION%%.*} -m pip install \
  -r "$ROOT/requirements-lambda.txt" \
  -t "$BUILD_DIR" \
  --upgrade \
  --only-binary=:all: 2>/dev/null || \
python${PYTHON_VERSION%%.*} -m pip install \
  -r "$ROOT/requirements-lambda.txt" \
  -t "$BUILD_DIR" \
  --upgrade

(
  cd "$BUILD_DIR"
  zip -qr "$OUTPUT_ZIP" .
)

echo "Created $OUTPUT_ZIP ($(du -h "$OUTPUT_ZIP" | awk '{print $1}'))"
