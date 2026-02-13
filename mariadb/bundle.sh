#!/bin/bash
# Exit on any error
set -e

# Ensure we are running from the script's directory
cd "$(dirname "$0")"

# Create a clean deployment directory
rm -rf deploy_mariadb
mkdir -p deploy_mariadb/wheels

# Copy the code and make it executable
cp db_failover.py deploy_mariadb/
chmod +x deploy_mariadb/db_failover.py
cp requirements.txt deploy_mariadb/

echo "Downloading dependencies for RedHat 9 (Python 3.9)..."
# We add --implementation and --abi to be extremely specific for RHEL 9
# manylinux_2_28 is also highly compatible with RHEL 9 (glibc 2.34)
pip download \
    --only-binary=:all: \
    --platform manylinux_2_28_x86_64 \
    --implementation cp \
    --python-version 3.9 \
    --abi cp39 \
    -d ./deploy_mariadb/wheels \
    -r requirements.txt

# Verify that wheels were actually downloaded
if [ "$(ls -A deploy_mariadb/wheels)" = "" ]; then
    echo "ERROR: No wheels were downloaded. Check your internet connection or pip version."
    exit 1
fi

# Create a single archive for transfer
tar -czvf mariadb_failover_bundle.tar.gz deploy_mariadb

echo "----------------------------------------------------------"
echo "Bundle created: mariadb_failover_bundle.tar.gz"
echo "Wheels included: $(ls deploy_mariadb/wheels | wc -l)"
echo "Done! Transfer the .tar.gz to the target system."
