"""
MariaDB Connection Pool Failover Example.

This script demonstrates how to handle Virtual IP (VIP) failovers using the
MariaDB Python Connector's ConnectionPool. It explicitly shows how stale
connections are discarded and refreshed when the VIP switches nodes.
"""

import sys
import time
import uuid
import mariadb

# Configuration for the MariaDB connection
# pool_validation_interval=0 ensures that every time you call get_connection(),
# the connector pings the server to verify the connection is still alive.
DB_CONFIG = {
    "host": "127.0.0.1",  # Replace with your VIP
    "user": "root",
    "password": "secret",
    "database": "test",
    "port": 3306,
    "pool_name": "vip_pool",
    "pool_size": 5,
    "pool_validation_interval": 0,
}


def create_pool():
    """
    Initializes the connection pool and creates the test table.
    """
    try:
        print(f"Initializing connection pool '{DB_CONFIG['pool_name']}'...")
        pool = mariadb.ConnectionPool(**DB_CONFIG)

        # Initialize schema
        with pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS failover_test (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        node_name VARCHAR(255),
                        event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        test_uuid VARCHAR(36)
                    )
                """)
        return pool
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)


def run_example():
    """
    Runs a continuous loop performing INSERT and SELECT operations.
    Detects and reports when the VIP switches to a different physical node.
    """
    pool = create_pool()
    last_node = None

    print("-" * 60)
    print(f"Monitoring VIP: {DB_CONFIG['host']}")
    print("The script will detect and report node changes automatically.")
    print("-" * 60)

    while True:
        try:
            # get_connection() performs validation because pool_validation_interval=0.
            # Stale connections are automatically dropped and replaced here.
            with pool.get_connection() as conn:
                conn_id = id(conn)
                with conn.cursor() as cursor:
                    # 1. Identify current node
                    cursor.execute("SELECT @@hostname")
                    hostname = cursor.fetchone()[0]

                    # Detect node switch
                    if last_node and hostname != last_node:
                        print("\n" + "!" * 60)
                        print("  [ALARM] VIP SWITCH DETECTED!")
                        print(f"  Old Node: {last_node}")
                        print(f"  New Node: {hostname}")
                        print("  Action:   Stale connections discarded. Pool refreshed.")
                        print("!" * 60 + "\n")
                    last_node = hostname

                    # 2. Perform a Write
                    current_uuid = str(uuid.uuid4())
                    cursor.execute(
                        "INSERT INTO failover_test (node_name, test_uuid) VALUES (%s, %s)",
                        (hostname, current_uuid),
                    )
                    conn.commit()

                    # 3. Perform a Read to verify
                    cursor.execute(
                        "SELECT id, event_time FROM failover_test WHERE test_uuid = %s",
                        (current_uuid,),
                    )
                    result = cursor.fetchone()
                    if result:
                        row_id, ts = result
                        print(f"[OK] Node: {hostname:<15} | ConnID: {str(conn_id)[-4:]} | "
                              f"Row: {row_id:<5} | Pool: {pool.connection_count}/{pool.pool_size} | {ts}")

        except mariadb.OperationalError as e:
            print(f"[WAIT] Connection lost ({e.errno}). VIP is switching. "
                  "Pool will refresh on next attempt...")
        except mariadb.Error as e:
            print(f"[ERROR] MariaDB Error: {e}")

        time.sleep(2)


if __name__ == "__main__":
    run_example()
