Install dependencies:

    pipenv install -r requirements.txt

Try:

    pipenv shell

Run:

    python dbpulse.py

Modify `dbconfig` to match your server:

    dbconfig = {
            "host": "127.0.0.1",
            "database": "world",
            "user":     "root",
            "password": "test"
            }
