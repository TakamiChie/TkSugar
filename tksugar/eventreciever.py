class EventReciever(object):
  def __init__(self, object, tag, callback):
    self.object = object
    self.tag = tag
    self.callback = callback

  def __call__(self, event=None):
    self.callback(self.object, self.tag)