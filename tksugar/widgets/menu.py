import tkinter

from tksugar.widgets.generatorsupport import GeneratorSupport
from tksugar.eventreciever import EventReciever

class Menu(tkinter.Menu, GeneratorSupport):
  """
  `tkinter.Menu` with added methods to support Generator.
  """
  def __init__(self, master=None, cnf={}, **kw):
    """Construct menu widget with the parent MASTER.

    Valid resource names: activebackground, activeborderwidth,
    activeforeground, background, bd, bg, borderwidth, cursor,
    disabledforeground, fg, font, foreground, postcommand, relief,
    selectcolor, takefocus, tearoff, tearoffcommand, title, type."""
    super().__init__(master=None, cnf=cnf, **kw)
    self._command = None
    self._parent = None
    if issubclass(type(master), tkinter.Wm):
      master.config(menu=self)

  def append_child(self, child, **params):
    params["menu"] = child
    child._parent = self
    self.add_cascade(params)

  def items(self, items):
    """
    Define a menu item.

    Parameters
    ----
    items: list(str or dict)
      An array of menu items. Information defining a string or menu item.
    """
    def radio(a):
      for n, i in enumerate(a["items"]):
        self.add_radiobutton(
          label= i["label"] if type(i) is dict else i,
          variable=a.get("variable", None),
          value= i.get("value", n) if type(i) is dict else n,
          command= a.get("command", None))
    def cascade(a):
      items = a.pop("items")
      tearoff = a.pop("tearoff", False)
      m = Menu(master=self, tearoff=tearoff)
      m.items(items)
      self.append_child(m, **a)
    for item in items:
      if type(item) is str:
        if item == "---":
          item = {
            "type": "separator"
          }
        else:
          item = {
            "type": "command",
            "label": item
          }
      item.setdefault("type", "command")
      if "name" in item and not "command" in item: item["command"] = EventReciever(self, item["name"], self._callback)
      if "label" in item and not "command" in item: item["command"] = EventReciever(self, item["label"], self._callback)
      if "name" in item: item.pop("name")
      switch = {
        "separator": lambda a: self.add_separator(),
        "command": lambda a: self.add_command(a),
        "check": lambda a: self.add_checkbutton(a),
        "radio": lambda a: radio(a),
        "cascade": lambda a: cascade(a)
      }
      t = item.pop("type")
      v = switch.get(t, ValueError)(item)
      if issubclass(type(v), Exception):
        raise v

  def _callback(self, o, n):
    """
    Callbacks for various menus.
    """
    if not self.command is None:
      self.command.tag.tag["item"] = n
      self.command()
    elif not self.parent is None:
      self.parent._callback(o, n)

  @property
  def parent(self):
    """
    Gets parent.
    """
    return self._parent

  @property
  def command(self):
    """
    Gets or sets an event handler that will be executed when the button is pressed.
    """
    return self._command

  @command.setter
  def command(self, value):
    """
    Gets or sets an event handler that will be executed when the button is pressed.
    """
    self._command = value
