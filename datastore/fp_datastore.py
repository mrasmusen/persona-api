"""
    Abstract class FakeProfileDataStore defines the three methods supported
    by a fake profiles data store.
    Also defines some exceptions to be user by fake profiles data stores.
"""

from abc import ABC, abstractmethod


class FakeProfilesDataStore(ABC):

    """
        Searches the datastore with a user with a given username.
        Returns Json data for that user if it exists, raises a
        ResourceNotFoundError if it doesn't.
    """
    @abstractmethod
    def get_single_user(self, username):
        pass

    """
        Returns all users within a given range, defined by start_index
        and page_size, in the datastore. Doesn't specify how the results
        are to be sorted, but the sorting must be consistent across
        multiple calls.
        Raises a DataOutOfRangeError if the supplied page boundaries
        are out of the range of the data.
    """
    @abstractmethod
    def get_all_users(self, start_index, page_size):
        pass

    """
        Deletes a user with the given username.
        Raises a ResourceNotFoundError if the user doesn't exist.
    """
    @abstractmethod
    def delete_single_user(self, username):
        pass

    """
        Method to load the data from an unzipped json file into
        the database.
    """
    @abstractmethod
    def add_data_from_json_file(self, jsonfile):
        pass


class NoDataStoreError(Exception):
    pass


class ResourceNotFoundError(Exception):
    pass


class UnknownDataStoreError(Exception):
    pass


class DataOutOfRangeError(Exception):
    pass
