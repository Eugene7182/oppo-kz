import json,os
from jsonschema import validate
SCHEMA_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..','docs','v2.2'))
_cache={}
def _load(name:str):
  if name not in _cache:
    with open(os.path.join(SCHEMA_DIR,name),'r',encoding='utf-8') as f:
      _cache[name]=json.load(f)
  return _cache[name]
def validate_row(schema_file:str,row:dict):
  validate(instance=row,schema=_load(schema_file))
