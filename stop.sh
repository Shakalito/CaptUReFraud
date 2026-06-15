#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "Stopping CaptUReFraud services..."
docker compose down
echo "Services stopped."