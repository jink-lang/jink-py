
class FutureIter:
  def __init__(self, i):
    self._input = i
    self._iter = iter(i)
    self._future()

  def __str__(self):
    return self._input

  def _future(self):
    try:
      self.next = next(self._iter)
    except StopIteration:
      self.next = None

  def _next(self):
    t = self.next
    self._future()
    return t
