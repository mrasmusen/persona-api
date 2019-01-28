import falcon
import json

from fp_datastore import ResourceNotFoundError, DataOutOfRangeError
from fp_dummy_datastore import DummyFPDataStore
from fp_server import AllUsersResource, SingleUserResource

"""
  Create a single instance of each resource type for testing. This is 
  how Falcon uses it's resources, so this is the most representative
  case.
"""
all_users = AllUsersResource(DummyFPDataStore())
single_user = SingleUserResource(DummyFPDataStore())  

def are_dicts_equal(a, b):
  shared_items = {a[k] for k in a.keys() if k in b.keys() and a[k] == b[k]}
  if len(shared_items) == len(a):
    return True
  else:
    return False

class DummyReq(object):
  def __init__(self, params=None):
    self.params = params

class DummyResp(object):
  def __init__(self):
    self.body = None
    self.status = None
    self.content_type = None

# Check we get the correct data back from the db
def test_succesful_get_single():
  req = DummyReq()
  resp = DummyResp()
  
  single_user.on_get(req, resp, "hello")

  assert resp.status == falcon.HTTP_200
  assert are_dicts_equal(json.loads(resp.body), {"username": "hello", "pet": "Dog"})

# Check a failure from the db returns 404
def test_fail_get_single():
  req = DummyReq()
  resp = DummyResp()
  
  single_user.on_get(req, resp, "notfound")

  assert resp.status == falcon.HTTP_404




