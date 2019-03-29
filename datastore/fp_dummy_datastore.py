"""
    Dummy implementation of FakeProfilesDataStore used to test
    the routing in the server. No storage takes place, data is
    generated on the spot. Some values can cause the dummy store
    to raise errors. The schema is arbitrary and isn't related
    to the actual data the fake profiles use.
"""
from datastore.fp_datastore import (
    FakeProfilesDataStore,
    ResourceNotFoundError,
    DataOutOfRangeError
)

import random


class DummyFPDataStore(FakeProfilesDataStore):
    def __init__(self):
        pass

    """
        Returns successfully a dict with data in it.
        If the username is 'notfound' then the function
        will raise a ResourceNotFoundError.
    """
    def get_single_user(self, username):
        if username == "notfound":
            raise ResourceNotFoundError()
        else:
            return build_random_user(username=username)

    """
        Returns users with username 'fake_person_X' where
        x is their index in the database. If the index is
        over 99 then raise DataOutOfRangeError.
    """
    def get_all_users(self, start_index, page_size):
        if start_index + page_size >= 100:
            raise DataOutOfRangeError()
        else:
            users = []
        for i in range(page_size):
            users.append(build_random_user(number=i))
        return users

    """
        If username is 'notfound', return a ResourceNotFoundError.
        Otherwise do nothing.
    """
    def delete_single_user(self, username):
        if username == "notfound":
            raise ResourceNotFoundError()

    def add_single_user(self, data):
        pass

    def add_data_from_json_file(self, jsonfile):
        pass


def build_random_user(username="user", number=None):
    return {
        "job": "SomeJob",
        "company": "Company, Inc",
        "ssn": "123456789",
        "residence": "123 My Street, SE3 4AB",
        "current_location": [
            float(random.randint(12345, 98765)),
            float(random.randint(12345, 98765))
        ],
        "blood_group": "A+-",
        "website": [
            "a.com",
            "b.co.uk"
        ],
        "username": "{}{}{}".format(
            username, '_' if number is not None else '', number
        ),
        "name": "User Name",
        "sex": "M/F",
        "address": "456 Another Street, No postcode",
        "mail": "user@name.com",
        "birthdate": "01-01-2000"
    }
