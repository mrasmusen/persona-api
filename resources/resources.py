import falcon
import json
import os
import time
import zipfile

from datastore.fp_dummy_datastore import DummyFPDataStore
from datastore.fp_json_blob_datastore import JsonBlobDataStore
from datastore.fp_sql_datastore import SqlDataStore
from datastore.fp_datastore import FakeProfilesDataStore, ResourceNotFoundError, DataOutOfRangeError

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
			resp.status = falcon.HTTP_400
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