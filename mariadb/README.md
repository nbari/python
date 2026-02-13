# MariaDB VIP Failover Example

This example demonstrates how to use the MariaDB Python Connector's
`ConnectionPool` to handle Virtual IP (VIP) failovers in an active-active or
active-passive MariaDB cluster.

## Key Feature: `pool_validation_interval`

The script uses `pool_validation_interval=0`. This setting ensures that every
time `pool.get_connection()` is called, the connector pings the database. If
the VIP has moved to a different node, the existing TCP connection will be
invalid; the connector detects this via the failed ping and automatically
establishes a new connection to the VIP (which now routes to the healthy node).

## Transferring to the Offline System

### 1. Bundle on a machine WITH internet
Run the bundle script to download the code and the specific pre-compiled binaries for RedHat 9:

```bash
chmod +x bundle.sh
./bundle.sh
```

This creates a file named `mariadb_failover_bundle.tar.gz`.

### 2. Copy to the Target System
Use a USB drive, `scp`, or your preferred internal transfer method to move `mariadb_failover_bundle.tar.gz` to the offline server.

### 3. Install on the Offline System
Once the file is on the target server:

```bash
# Extract the bundle
tar -xzvf mariadb_failover_bundle.tar.gz
cd deploy_mariadb

# Install using the local wheels (no internet required)
pip3 install --no-index --find-links=./wheels -r requirements.txt
```

## Running the Example
Update the `db_config` in `db_failover.py` with your VIP address and credentials, then run:
```bash
python3 db_failover.py
```
