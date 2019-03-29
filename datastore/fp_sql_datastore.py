"""
    Implementation of FakeProfilesDataStore using sqlite3 to create a local
    database. This allows us to abstract away the actual data access and
    don't need to worry about altering a large json file.

    When the class is created, any existing database is cleared and the
    caller can then load in new json from the zip file.

    The database has 2 tables - one for users and a second for websites,
    since the websites attribute has a variable length between users.
"""

import os
import mysql.connector
import traceback

from datastore.fp_datastore import (
    FakeProfilesDataStore,
    ResourceNotFoundError,
    DataOutOfRangeError,
    NoDataStoreError
)


class SqlDataStore(FakeProfilesDataStore):
    def __init__(self):
        self.db_conn_data = None
        try:
            self.db_conn_data = {
                "user": os.getenv("MYSQL_SERVICE_USER", "persona_user"),
                "password": os.getenv("MYSQL_SERVICE_PASSWORD", "password"),
                "host": os.getenv("MYSQL_SERVICE_HOST", "localhost"),
                "database": os.getenv("MYSQL_SERVICE_PERSONA_DB", "personadb")
            }
        except Exception:
            traceback.print_exc()
            self.db_conn_data = None

    def get_single_user(self, username):
        if self.db_conn_data is None:
            raise NoDataStoreError

        db = mysql.connector.connect(**self.db_conn_data)
        cursor = db.cursor()

        cursor.execute("""
                SELECT * from users WHERE username=%s;
            """, (username, ))

        """
            Need to get the websites data in separate calls, since
            sqlite3 doesn't support FULL OUTER JOINs in python.
        """
        users_data = cursor.fetchall()
        websites_data = {}
        for user in users_data:
            cursor.execute("""
                SELECT website from websites WHERE user_id=%s;
            """, (user[0], ))

            websites_data[user[0]] = cursor.fetchall()

        return self.format_rows_into_json(users_data, websites_data)

    def get_all_users(self, start_index, page_size):
        if self.db_conn_data is None:
            raise NoDataStoreError

        db = mysql.connector.connect(**self.db_conn_data)
        cursor = db.cursor()

        cursor.execute("""
                SELECT * from users WHERE id>=%s AND id<%s;
            """, (start_index, start_index + page_size))

        """
            Need to get the websites data in separate calls, since
            sqlite3 doesn't support FULL OUTER JOINs in python.
        """
        users_data = cursor.fetchall()
        websites_data = {}
        for user in users_data:
            # print(user)
            cursor.execute("""
                SELECT website from websites WHERE user_id=%s;
            """, (user[0], ))

            websites_data[user[0]] = cursor.fetchall()

        return self.format_rows_into_json(users_data, websites_data)

    def delete_single_user(self, username):
        if self.db_conn_data is None:
            raise NoDataStoreError

        db = mysql.connector.connect(**self.db_conn_data)
        cursor = db.cursor()

        cursor.execute("""
                DELETE FROM users WHERE username=%s
            """, (username, ))

        db.commit()

    def add_single_user(self, data):
        pass

    """
        Takes the raw database output and formats it into the json
        the user expects.
    """

    def format_rows_into_json(self, rows, websites):
        if self.db_conn_data is None:
            raise NoDataStoreError

        json_list = []
        for row in rows:
            json_list.append(self.format_row_into_json(row, websites[row[0]]))

        return json_list

    """
        Build single json item from raw data.
    """
    def format_row_into_json(self, row, websites):
        if self.db_conn_data is None:
            raise NoDataStoreError

        return {
            "job": row[1],
            "company": row[2],
            "ssn": row[3],
            "residence": row[4],
            "current_location": [
                row[5],
                row[6]
            ],
            "blood_group": row[7],
            "website": [w[0] for w in websites],
            "username": row[8],
            "name": row[9],
            "sex": row[10],
            "address": row[11],
            "mail": row[12],
            "birthdate": row[13]
        }

    def add_data_from_json_file(self, jsonfile):
        pass

    def __del__(self):
        if self.db_conn_data is None:
            raise NoDataStoreError

        db = mysql.connector.connect(**self.db_conn_data)
        db.close()
