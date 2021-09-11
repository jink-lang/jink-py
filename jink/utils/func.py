import jsonpickle

def pickle(obj):
  encoded = jsonpickle.encode(obj, unpicklable=False)
  return jsonpickle.decode(encoded)
