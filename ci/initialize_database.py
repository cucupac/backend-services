import time
import os
from datetime import datetime

import psycopg2
import click


DB_CONNECTION_TIMEOUT = 10
CONNECTION_INFO = {
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_USER"),
    "port": os.getenv("POSTGRES_PORT"),
}


def connect_to_db():
    """Attempt to connect to test database within specified amount of time."""

    start_time = time.monotonic()

    errors = []
    while time.monotonic() - start_time <= DB_CONNECTION_TIMEOUT:
        try:
            db_connection = psycopg2.connect(**CONNECTION_INFO)
            with db_connection:
                print("CONNECTED TO TEST DATABASE🙂")
                break
        except psycopg2.OperationalError as error:
            errors.append(f"{datetime.utcnow()}: {str(error)}")

        time.sleep(1)
    else:
        click.secho(
            f"ERROR: It took longer than {DB_CONNECTION_TIMEOUT} seconds "
            "to connect to the test database. See attempt errors below:\n",
            fg="red",
            bold=True,
        )
        for error in errors:
            print(error)
        raise SystemExit(1)


def create_schema():
    """Creates schemas."""

    db_connection = psycopg2.connect(**CONNECTION_INFO)
    cursor = db_connection.cursor()
    db_connection.set_isolation_level(0)

    try:
        cursor.execute(f"CREATE SCHEMA wh_relayer;")
        cursor.execute(f"CREATE SCHEMA ax_scan;")
        cursor.execute(f"CREATE SCHEMA gas_system;")
    except Exception as e:
        click.secho(
            f"ERROR: There was an error creating a database schema:\n{e}",
            fg="red",
            bold=True,
        )
        raise SystemExit(1)

    cursor.close()
    db_connection.close()


if __name__ == "__main__":
    connect_to_db()
    create_schema()
