import tkinter

from tksugar.widgets.generatorsupport import GeneratorSupport

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
    if issubclass(type(master), tkinter.Wm):
      master.config(menu=self)

  def append_child(self, child, **params):
    params["menu"] = child
    self.add_cascade(params)

  def items(self, items):
    """
    Define a menu item.

    Parameters
    ----
    items: list(str or dict)
      An array of menu items. Information defining a string or menu item.
    """
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
      switch = {
        "separator": lambda a: self.add_separator(),
        "command": lambda a: self.add_command(a),
        "check": lambda a: self.add_checkbutton(a),
        "radio": lambda a: [self.add_radiobutton(label= i["label"] if type(i) is dict else i,
            variable=a.get("variable", None),
            value= i.get("value", n) if type(i) is dict else n) for n, i in enumerate(a["items"])]
      }
      t = item.pop("type")
      v = switch.get(t, ValueError)(item)
      if issubclass(type(v), Exception):
        raise v