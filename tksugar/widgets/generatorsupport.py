from abc import abstractmethod

class GeneratorSupport(object):
  """
  An abstract class that defines methods to support your own custom processing.
  Generator compatible class inherits this class and implements necessary methods.
  """

  @abstractmethod
  def append_child(self, child, **params):
    """
    Called when storing a child object.

    Parameters
    ----
    child: tkinter.Widget
      A list of objects that are child elements of the object.
    params: dict
      Parameters.
    """
    raise NotImplementedError