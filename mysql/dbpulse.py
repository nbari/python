import mysql.connector.pooling
import random
import time
import uuid

def loop(conn):
    db = conn.cursor(prepared=True)

    # This will create table dbpulse_rw if it doesn't exists
    db.execute('''CREATE TABLE IF NOT EXISTS dbpulse_rw (
            id INT NOT NULL,
            t1 INT(11) NOT NULL ,
            t2 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            uuid CHAR(36) CHARACTER SET ascii,
            UNIQUE KEY(uuid),
            PRIMARY KEY(id)) ENGINE=InnoDB''')

    r_id  =  random.randint(0,100)
    now   = int(time.time())
    uid   = uuid.uuid1()

    # write into table
    stmt = "INSERT INTO dbpulse_rw (id, t1, uuid) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE t1=%s, uuid=%s"
    args = (r_id, now, str(uid), now, str(uid),)
    try:
        db.execute(stmt,args)
        conn.commit()
    except Exception as e:
        print(e)

    # read data
    stmt = "SELECT t1, uuid FROM dbpulse_rw WHERE id=%s"
    args = (r_id,)
    try:
        db.execute(stmt,args)
        records = db.fetchall()
        for row in records:
            if row[0] != now or row[1] != str(uid):
                exit("no match")
    except Exception as e:
        print(e)

    return (r_id, now, uid)

if __name__ == "__main__":
    dbconfig = {
            "host": "127.0.0.1",
            "database": "world",
            "user":     "root",
            "password": "test"
            }

    conn = mysql.connector.connect(pool_name = "mypool",
            pool_size = 3, connection_timeout=90,
            **dbconfig)

    while True:
        rs = loop(conn)
        print("id: %+2s, timestamp: %s, uuid: %s" % (rs[0], rs[1], rs[2]))
        time.sleep(1)
