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

from falcon_swagger_ui import register_swaggerui_app

import pathlib

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

page_title = "Falcon Swagger Doc"
favicon_url = 'https://falconframework.org/favicon-32x32.png'

SCHEMA_URL = '/static/v1/swagger_api.yml'
STATIC_PATH = pathlib.Path(__file__).parent / 'static'

SWAGGERUI_URL = '/swagger'

app.add_static_route('/static', str(STATIC_PATH))


register_swaggerui_app(
    app, SWAGGERUI_URL, SCHEMA_URL,
    page_title=page_title,
    favicon_url=favicon_url,
    config={'supportedSubmitMethods': ['get', 'delete'], }
)
