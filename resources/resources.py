import falcon
import json
import os
import time
import zipfile

from datastore.fp_datastore import (
    FakeProfilesDataStore,
    ResourceNotFoundError,
    DataOutOfRangeError,
    NoDataStoreError
)


class AllUsersResource(object):
    def __init__(self, datastore):
        self.datastore = datastore

    def on_get(self, req, resp):
        try:
            """
                Parse the parameters, getting start and pagesize
                to get all users.
            """
            start_index = int(req.params["start"])
            page_size = int(req.params["pagesize"])
            data = self.datastore.get_all_users(start_index, page_size)
            resp.body = json.dumps(data)
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_200
        except DataOutOfRangeError:
            resp.status = falcon.HTTP_400
            resp.content_type = falcon.MEDIA_TEXT
            resp.body = "Data out of range!"
        except (KeyError, ValueError):
            resp.status = falcon.HTTP_400
            resp.content_type = falcon.MEDIA_TEXT
            resp.body = "Required parameters: start<int> and pagesize<int>"
        except NoDataStoreError:
            resp.status = falcon.HTTP_500
            resp.content_type = falcon.MEDIA_TEXT
            resp.body = "Not connected to database."

    def on_post(self, req, resp):
        resp.content_type = falcon.MEDIA_TEXT
        try:
            data = json.loads(req.stream.read().decode('utf-8'))
            self.datastore.add_single_user(data)
            resp.status = falcon.HTTP_201
            resp.body = "User successfully added."
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.body = "Unspecified error when saving data."
            raise(e)


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
            resp.content_type = falcon.MEDIA_TEXT
            resp.body = "User not found."
        except NoDataStoreError:
            resp.content_type = falcon.MEDIA_TEXT
            resp.status = falcon.HTTP_500
            resp.body = "Not connected to database."

    def on_delete(self, req, resp, username):
        try:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_TEXT
            self.datastore.delete_single_user(username)
            resp.body = "Deleted successfully."
        except ResourceNotFoundError:
            resp.content_type = falcon.MEDIA_TEXT
            resp.status = falcon.HTTP_404
            resp.body = "User not found."


class ComplexUserRequestResource(object):
    def __init__(self, datastore):
        self.datastore = datastore

    def on_get(self, req, resp):
        try:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            num_websites = int(req.params["numWebsites"])
            job = req.params["job"]
            pagesize = -1
            if "pagesize" in req.params:
                pagesize = int(req.params["pagesize"])
            resp.body = json.dumps(
                self.datastore.get_complex_request(
                    num_websites=num_websites,
                    job=job,
                    pagesize=pagesize
                ))
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.body = "Unspecified error when saving data."
            raise(e)
