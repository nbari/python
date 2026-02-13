#!/bin/bash
set -e
cd "$(dirname "$0")"

rm -rf deploy_mariadb
mkdir -p deploy_mariadb/wheels
mkdir -p deploy_mariadb/rpms

echo "Building MariaDB Bundle for RHEL 9 (with C-library upgrade)..."
podman run --rm \
    -v "$(pwd)/deploy_mariadb/wheels:/output_wheels:Z" \
    -v "$(pwd)/deploy_mariadb/rpms:/output_rpms:Z" \
    rockylinux:9 bash -c "
    echo 'Installing tools...'
    dnf install -y --allowerasing curl gcc python3-devel python3-pip dnf-plugins-core
    
    echo 'Adding official MariaDB repository...'
    curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash -s -- --skip-maxscale
    
    echo 'Downloading MariaDB C-Connector RPMs for upgrade...'
    # Use dnf download (provided by dnf-plugins-core)
    dnf download -y --destdir=/output_rpms MariaDB-shared MariaDB-common
    
    echo 'Installing MariaDB-devel for build...'
    dnf install -y MariaDB-devel
    
    echo 'Building wheel...'
    pip3 wheel mariadb -w /output_wheels
"

echo "Downloading dependencies..."
pip3 download -d ./deploy_mariadb/wheels packaging

cp db_failover.py deploy_mariadb/
chmod +x deploy_mariadb/db_failover.py

cat << 'EOF' > deploy_mariadb/install.sh
#!/bin/bash
set -e
echo "1. Upgrading MariaDB C-Library to compatible version..."
# Use --allowerasing to handle conflicts with the old system library
sudo dnf install -y --allowerasing ./rpms/MariaDB-*.rpm

echo "2. Installing MariaDB Python connector..."
pip3 install --no-index --find-links=./wheels mariadb packaging

echo "Done! The system now has the correct C-library and Python connector."
echo "Run with: ./db_failover.py"
EOF
chmod +x deploy_mariadb/install.sh

tar -czvf mariadb_failover_bundle.tar.gz deploy_mariadb
echo "----------------------------------------------------------"
echo "Bundle created: mariadb_failover_bundle.tar.gz"
echo "----------------------------------------------------------"
