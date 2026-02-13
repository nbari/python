#!/bin/bash
# Run this on a machine WITH internet access

# Create a clean deployment directory
mkdir -p deploy_mariadb/wheels

# Copy the code
cp db_failover.py deploy_mariadb/
cp requirements.txt deploy_mariadb/

echo "Downloading dependencies for RedHat 9 (Python 3.9)..."
# --platform: manylinux_2_34_x86_64 is compatible with RHEL 9
# --python-version: 3.9 (Standard RHEL 9 python)
# --only-binary: :all: ensures we don't get source files that need compiling
pip download \
    --only-binary=:all: \
    --platform manylinux_2_34_x86_64 \
    --python-version 3.9 \
    -d ./deploy_mariadb/wheels \
    -r requirements.txt

# Create a single archive for transfer
tar -czvf mariadb_failover_bundle.tar.gz deploy_mariadb

echo "----------------------------------------------------------"
echo "Done! Transfer 'mariadb_failover_bundle.tar.gz' to the target system."
