import falcon
import json
import os
import time
import zipfile

from fp_dummy_datastore import DummyFPDataStore
from fp_json_blob_datastore import JsonBlobDataStore
from fp_sql_datastore import SqlDataStore
from fp_datastore import FakeProfilesDataStore, ResourceNotFoundError, DataOutOfRangeError

class AllUsersResource(object):
	def __init__(self, datastore):
		self.datastore = datastore
	
	def on_get(self, req, resp):
		try:
			"""
				Parse the parameters, getting start and pagesize to get all users.
			"""
			start_index = int(req.params["start"])
			page_size = int(req.params["pagesize"])
			resp.body = json.dumps(self.datastore.get_all_users(start_index, page_size))
			resp.content_type = falcon.MEDIA_JSON
			resp.status = falcon.HTTP_200
		except DataOutOfRangeError:
			resp.status = falcon.HTTP_404
			resp.body = "Data out of range!"
		except (KeyError, ValueError):
			resp.status = falcon.HTTP_400
			resp.body = "Required parameters: start<int> and pagesize<int>"

class SingleUserResource(object):
	def __init__(self, datastore):
		self.datastore = datastore

	def on_get(self, req, resp, username):
		try:
			resp.status = falcon.HTTP_200
			resp.content_type = falcon.MEDIA_JSON
			resp.body = json.dumps(self.datastore.get_single_user(username))
		except ResourceNotFoundError:
			resp.status = falcon.HTTP_404
			resp.body = "User not found."

	def on_delete(self, req, resp, username):
		try:
			resp.status = falcon.HTTP_200
			self.datastore.delete_single_user(username)
			resp.body = "Deleted successfully."
		except ResourceNotFoundError:
			resp.status = falcon.HTTP_404
			resp.body = "User not found."
		
def unzip_json_file(filepath):
	zipper = zipfile.ZipFile(filepath)
	json_path = os.path.dirname(os.path.realpath(__file__))
	extracted_filename = zipper.namelist()[0]
	zipper.extractall(json_path)
	zipper.close()
	return os.path.join(json_path, extracted_filename)

# Create a data store and add the json data from the file
ds = SqlDataStore()
ds.add_data_from_json_file(unzip_json_file("./fake_profiles.zip"))

app = falcon.API()

# Set up resources
all_users_resourse = AllUsersResource(ds)
single_user_resource = SingleUserResource(ds)

# Add routes to app
app.add_route("/users", all_users_resourse,)
app.add_route("/users/{username}", single_user_resource)