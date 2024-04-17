import os
import jsonpickle

def pickle(obj):
  encoded = jsonpickle.encode(obj, unpicklable=False)
  return jsonpickle.decode(encoded)

def get_path():
  return os.getcwd().replace('\\', '/')
