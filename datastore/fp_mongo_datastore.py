"""
  Implementation of FP_Datastore class that uses mongoDb.
"""

import json
import os
import traceback

from mongoengine import (
    connect,
    Document,
    StringField,
    ListField,
    FloatField
)

from bson import ObjectId

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
        query_result = PersonaUser.objects(username=username)
        print(type(query_result))
        return build_json_from_query(query_result)

    def get_all_users(self, start_index, page_size):
        query_result = PersonaUser.objects()[start_index:start_index+page_size]
        return build_json_from_query(query_result)

    def delete_single_user(self, username):
        retval = PersonaUser.objects(username=username).delete()
        if retval is 0:
            # Mirrors other implementations by raising an error if the user
            # tries to delete a document that's not present
            raise ResourceNotFoundError

    def add_single_user(self, data):
        # Don't even bother doing any error checking.
        PersonaUser(**data).save()

    def get_complex_request(self, num_websites=0, job="", pagesize=5):
        agg_query = [
            {
                '$project': {
                    'username': True,
                    'name': True,
                    'ssn': True,
                    'job': True,
                    'current_location': True,
                    'website': True,
                    'websiteNumCmp': {
                        '$gte': [
                            {
                                '$size': '$website'
                            }, num_websites
                        ]
                    }
                }
            }, {
                '$match': {
                    'job': job,
                    'websiteNumCmp': True
                }
            }, {
                '$redact': {
                    '$cond': {
                        'if': {
                            '$gt': [
                                {'$strLenCP': '$name'}, 15
                            ]
                        },
                        'then': '$$KEEP',
                        'else': '$$PRUNE'
                    }
                }
            }, {
                '$sort': {
                    'ssn': -1
                }
            }, {
                '$project': {
                    'websiteNumCmp': False,
                    'job': False
                }
            }, {
                '$unwind': '$website'
            }
        ]

        if pagesize > 0:
            agg_query.insert(3, {
                '$limit': pagesize
            })

        query_result = PersonaUser.objects.aggregate(*agg_query)
        res_json = []
        for item in query_result:
            item.pop("_id", None)
            res_json.append(item)
        return res_json

    def add_data_from_json_file(self, jsonfile):
        pass
        # with open(jsonfile) as f:s
        #   for item in json.loads(f.read()):
        #     PersonaUser(**item).save()


def build_json_from_query(query_result):
    query_dict = json.loads(query_result.to_json())
    for item in query_dict:
        item.pop("_id", None)
    return query_dict


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
