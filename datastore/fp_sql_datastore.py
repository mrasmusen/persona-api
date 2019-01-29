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
import sqlite3

from datastore.fp_datastore import FakeProfilesDataStore, ResourceNotFoundError, DataOutOfRangeError

class SqlDataStore(FakeProfilesDataStore):
  def __init__(self):
    self.data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "db")
    if os.path.isfile(self.data_path):
      os.remove(self.data_path)
    
    db = sqlite3.connect(self.data_path)
    cursor = db.cursor()
    
    cursor.execute("""
      CREATE TABLE users(id INTEGER PRIMARY KEY, job TEXT, company TEXT, ssn TEXT,
                         residence TEXT, longditude REAL, latitude REAL, 
                         blood_group TEXT, username TEXT, name TEXT, sex TEXT,
                         address TEXT, mail TEXT, birthdate TEXT)
    """)

    cursor.execute("""
      CREATE TABLE websites(id INTEGER PRIMARY KEY, user_id INTEGER, website TEXT)
    """)
  
  def get_single_user(self, username):
    db = sqlite3.connect(self.data_path)
    cursor = db.cursor()
    
    cursor.execute("""
      SELECT * from users WHERE username=:username;
    """, {"username": username})

    """
      Need to get the websites data in separate calls, since sqlite3 doesn't support
      FULL OUTER JOINs in python.
    """
    users_data = cursor.fetchall()
    websites_data = {}
    for user in users_data:
      cursor.execute("""
        SELECT website from websites WHERE user_id=:user_id;
      """, {"user_id": user[0]})

      websites_data[user[0]] = cursor.fetchall()

    return self.format_rows_into_json(users_data, websites_data)
  
  def get_all_users(self, start_index, page_size):
    db = sqlite3.connect(self.data_path)
    cursor = db.cursor()
    
    cursor.execute("""
      SELECT * from users WHERE id>=:start_idx AND id<:end_idx;
    """, {"start_idx": start_index, "end_idx": start_index + page_size})

    """
      Need to get the websites data in separate calls, since sqlite3 doesn't support
      FULL OUTER JOINs in python.
    """
    users_data = cursor.fetchall()
    websites_data = {}
    for user in users_data:
      cursor.execute("""
        SELECT website from websites WHERE user_id=:user_id;
      """, {"user_id": user[0]})

      websites_data[user[0]] = cursor.fetchall()

    return self.format_rows_into_json(users_data, websites_data)

  def delete_single_user(self, username):
    db = sqlite3.connect(self.data_path)
    cursor = db.cursor()
    
    cursor.execute("""
      DELETE FROM users WHERE username=:username
    """, {"username": username})

    db.commit()
  
  def add_data_from_json_file(self, jsonfile):
    db = sqlite3.connect(self.data_path)
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
        counter += 1
        cursor.execute("""
          INSERT INTO users(id, job, company, ssn, residence, longditude, latitude, 
                            blood_group, username, name, sex, address, mail, birthdate)

                          VALUES(:id, :job, :company, :ssn, :residence, :longditude, :latitude, 
                            :blood_group, :username, :name, :sex, :address, :mail, :birthdate)

        """, {"id": counter, "job": item["job"], "company": item["company"], "ssn": item["ssn"], "residence": item["residence"], 
              "longditude": float(item["current_location"][0]), "latitude": float(item["current_location"][1]), 
              "blood_group": item["blood_group"], "username": item["username"], "name": item["name"], 
              "sex": item["sex"], "address": item["address"], "mail": item["mail"], "birthdate": item["birthdate"]})

        for website in item["website"]:
          cursor.execute("""
            INSERT INTO websites(user_id, website) 
            VALUES(:user_id, :website)
          """, {"user_id": counter, "website": website})
        
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
    db = sqlite3.connect(self.data_path)
    db.close()