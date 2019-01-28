import json
import os
import zipfile

from fp_datastore import FakeProfilesDataStore, DataOutOfRangeError, ResourceNotFoundError

class JsonBlobDataStore(FakeProfilesDataStore):
  def __init__(self):
    self.data = {}


  def add_data_from_json_zip(self, filepath):
    zipper = zipfile.ZipFile(filepath)
    json_path = os.path.dirname(os.path.realpath(__file__))
    extracted_filename = zipper.namelist()[0]
    zipper.extractall(json_path)
    zipper.close()

    json_file = os.path.join(json_path, extracted_filename)
    raw_json = open(json_file).read()
    self.data = json.loads(raw_json)
  
  def get_single_user(self, username):
    users = []
    for user in self.data:
      if user["username"] == username:
        users.append(user)
    if len(users) > 0:
      return users
    else:
      raise ResourceNotFoundError
  
  def get_all_users(self, start_index, page_size):
    try:
      if page_size < 0:
        raise DataOutOfRangeError
      return self.data[start_index:start_index+page_size]
    except IndexError:
      raise DataOutOfRangeError

  def delete_single_user(self, username):
    got_user = False
    for i in range(len(self.data)-1, -1, -1):
      if self.data[i]["username"]  == username:
        self.data.pop(i)
        got_user = True
    if not got_user:
      raise ResourceNotFoundError