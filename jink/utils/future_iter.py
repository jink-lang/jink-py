class FutureIter:
  def __init__(self, i):
    self._input = i
    self._iter = iter(i)
    self._future()

  def __str__(self):
    return self._input

  def _future(self):
    try:
      self.current = next(self._iter)
    except StopIteration:
      self.current = None

  def _next(self):
    t = self.current
    self._future()
    return t
