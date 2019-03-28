"""
  Implementation of FP_Datastore class that uses mongoDb.
"""

import json
import os
import traceback

from mongoengine import connect, Document, StringField, ListField, FloatField

from datastore.fp_datastore import (
    FakeProfilesDataStore,
    ResourceNotFoundError,
    DataOutOfRangeError,
    NoDataStoreError
)


class MongoDataStore(FakeProfilesDataStore):
    def __init__(self):
        try:
            self.db_conn_data = {
                "username": os.getenv("MONGODB_SERVICE_USER", "persona_admin"),
                "password": os.getenv("MONGODB_SERVICE_PASSWORD", "password"),
                "host": os.getenv("MONGODB_SERVICE_HOST", "localhost"),
                "db": os.getenv("MONGODB_SERVICE_PERSONA_DB", "persona")
            }
        except Exception:
            traceback.print_exc()
            self.db_conn_data = None

        self.db = connect(**self.db_conn_data)

    def get_single_user(self, username):
        return PersonaUser.objects(username=username).to_json()

    def get_all_users(self, start_index, page_size):
        page_data = PersonaUser.objects()[start_index:start_index+page_size]
        return page_data.to_json()

    def delete_single_user(self, username):
        retval = PersonaUser.objects(username=username).delete()
        if retval is 0:
            # Mirrors other implementations by raising an error if the user
            # tries to delete a document that's not present
            raise ResourceNotFoundError

    def add_data_from_json_file(self, jsonfile):
        pass
        # with open(jsonfile) as f:s
        #   for item in json.loads(f.read()):
        #     PersonaUser(**item).save()


class PersonaUser(Document):
    job = StringField(required=True)
    company = StringField(required=True)
    ssn = StringField(required=True)
    residence = StringField(required=True)
    blood_group = StringField(required=True)
    username = StringField(required=True)
    name = StringField(required=True)
    sex = StringField(required=True)
    address = StringField(required=True)
    mail = StringField(required=True)
    birthdate = StringField(required=True)
    website = ListField(StringField(), required=True)
    current_location = ListField(FloatField(), required=True)
