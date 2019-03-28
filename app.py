import argparse
import configparser
import falcon
import os
import sys
import zipfile

from resources.resources import AllUsersResource, SingleUserResource
from datastore.fp_mongo_datastore import MongoDataStore
from datastore.fp_sql_datastore import SqlDataStore
from datastore.fp_dummy_datastore import DummyFPDataStore


# App will use the DATABASE_TYPE environment variable to know
# which DataStore adapter to use. Will default to using a
# dummy datastore.
db_type = os.getenv("DATABASE_TYPE", "dummy")

# Dictionary mapping environment variable data to datastore
# implementations.
supported_databases = {
    "dummy": DummyFPDataStore,
    "mysql": SqlDataStore,
    "mongodb": MongoDataStore
}

# Create a data store
try:
    datastore_implementation = supported_databases[db_type]
    ds = datastore_implementation()
    print("Connecting to '{}' database.".format(db_type))
except KeyError:
    print("'{}' is not a supported database type.".format(db_type))
    sys.exit(1)

# app variable needs to be globally accessible
app = falcon.API()

# Set up resources
all_users_resourse = AllUsersResource(ds)
single_user_resource = SingleUserResource(ds)

# # Add routes to app
app.add_route("/users", all_users_resourse,)
app.add_route("/users/{username}", single_user_resource)
