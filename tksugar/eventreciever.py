class EventReciever(object):
  def __init__(self, object, tag, callback):
    self.object = object
    self.tag = tag
    self.callback = callback

  def __call__(self, *args, **kw):
    name = self.tag if args == () else args[0]
    self.callback(self.object, name)