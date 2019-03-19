import falcon
import os
import zipfile

from resources.resources import AllUsersResource, SingleUserResource
from datastore.fp_sql_datastore import SqlDataStore

def unzip_json_file(filepath):
	zipper = zipfile.ZipFile(filepath)
	json_path = os.path.dirname(os.path.realpath(__file__))
	extracted_filename = zipper.namelist()[0]
	zipper.extractall(json_path)
	zipper.close()
	return os.path.join(json_path, extracted_filename)

# Create a data store and add the json data from the file
ds = SqlDataStore()
# ds.add_data_from_json_file(unzip_json_file("./fake_profiles.zip"))

# app variable needs to be globally accessible
app = falcon.API()

# Set up resources
all_users_resourse = AllUsersResource(ds)
single_user_resource = SingleUserResource(ds)

# Add routes to app
app.add_route("/users", all_users_resourse,)
app.add_route("/users/{username}", single_user_resource)