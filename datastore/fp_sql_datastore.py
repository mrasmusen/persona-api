"""
  Implementation of FakeProfilesDataStore using sqlite3 to create a local
  database. This allows us to abstract away the actual data access and 
  don't need to worry about altering a large json file.

  When the class is created, any existing database is cleared and the
  caller can then load in new json from the zip file.

  The database has 2 tables - one for users and a second for websites, 
  since the websites attribute has a variable length between users.
"""

import ijson
import os
import mysql.connector

from datastore.fp_datastore import FakeProfilesDataStore, ResourceNotFoundError, DataOutOfRangeError

MYSQL_DB_IP = "10.109.76.57" # todo env variable or something 

class SqlDataStore(FakeProfilesDataStore):
  def __init__(self):
    password_file = open("/etc/db-password/password.txt")
    db_password = password_file.read()
    self.db_conn_data = {
      "user": 'persona_user',
      "password": db_password,
      "host": os.environ["FOOLHARDY_LIGER_MYSQL_SERVICE_HOST"],
      "database": "personadb"
    }
    
  def get_single_user(self, username):
    db = mysql.connector.connect(**self.db_conn_data)
    cursor = db.cursor()
    
    cursor.execute("""
      SELECT * from users WHERE username=%s;
    """, (username, ))

    """
      Need to get the websites data in separate calls, since sqlite3 doesn't support
      FULL OUTER JOINs in python.
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
    db = mysql.connector.connect(**self.db_conn_data)
    cursor = db.cursor()
    
    cursor.execute("""
      SELECT * from users WHERE id>=%s AND id<%s;
    """, (start_index, start_index + page_size))

    """
      Need to get the websites data in separate calls, since sqlite3 doesn't support
      FULL OUTER JOINs in python.
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
    db = mysql.connector.connect(**self.db_conn_data)
    cursor = db.cursor()
    
    cursor.execute("""
      DELETE FROM users WHERE username=%s
    """, (username, ))

    db.commit()
  
  def add_data_from_json_file(self, jsonfile):
    db = mysql.connector.connect(**self.db_conn_data)
    cursor = db.cursor()
    
    print("Importing JSON data.")
    
    with open(jsonfile) as jf:
      counter = 0
      """
        Use ijson to iterate through the json data - the file is fairly big and using the
        default json module could cause memory issues. ijson is an iterative parser that
        allows us to stream in the file.
      """
      for item in ijson.items(jf, 'item'):
        """
          Explicitly set the id so we can add items to the websites database with the
          same counter as the user_id.
        """
        # print("Inserting item {}".format(counter))
        counter += 1
        if counter > 1000:
          break
        cursor.execute("""
          INSERT INTO users(id, job, company, ssn, residence, longditude, latitude, 
                            blood_group, username, name, sex, address, mail, birthdate)

                          VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

        """, (counter, item["job"], item["company"], item["ssn"], item["residence"], 
              float(item["current_location"][0]), float(item["current_location"][1]), 
              item["blood_group"], item["username"], item["name"], 
              item["sex"], item["address"], item["mail"],item["birthdate"]))

        for website in item["website"]:
          cursor.execute("""
            INSERT INTO websites(user_id, website) 
            VALUES(%s, %s)
          """, (counter, website))
    print("here")
    
    db.commit()

    print("Finished importing JSON.")
  
  """
    Takes the raw database output and formats it into the json the user expects.
  """
  def format_rows_into_json(self, rows, websites):
    json_list = []
    for row in rows:
      json_list.append(self.format_row_into_json(row, websites[row[0]]))

    return json_list
    
  """
    Build single json item from raw data.
  """
  def format_row_into_json(self, row, websites):
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
  
  def __del__(self):
    db = mysql.connector.connect(**self.db_conn_data)
    db.close()