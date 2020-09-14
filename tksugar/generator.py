import importlib
import inspect
import tkinter
from typing import Type

import yaml

from tksugar.tkmanager import TkManager

class TagData(object):
  """
  An object that represents additional data for the widget.
  In TkManager, it is used to link the TkManager ID and the widget.
  """
  def __init__(self, widget):
    """
    Constructor

    Parameters
    ----
    widget: object
      Tk widget.
    """
    self.widget = widget
    self.id = None
    self.tag= None

  def hasdata(self):
    """
    True if there is data.

    Returns
    ----
    hasdata: bool
      True if there is data
    """
    return self.id or self.tag

class EventReciever(object):
  def __init__(self, object, tag, callback):
    self.object = object
    self.tag = tag
    self.callback = callback

  def __call__(self, event=None):
    self.callback(self.object, self.tag)

class Generator(object):
  """
  The core object that creates the Tk window.
  Users of this module will use this core object to generate a Tk window.
  """
  def __init__(self, file="",modules=["tkinter"]):
    """
    constructor.

    Parameters
    ----
    file: str
      A file path describing the window's object and layout.
      This argument can be omitted, but in actual use it is not omitted in principle.
      Omitted only when testing.
    modules: list[str]
      An array indicating the name of the module to be used.
      By default, it is "tkinter" only.

      Because modules can be added with the `Generator#add_modules()`,
      the value is specified here only if you do not want to load the tkinter module.
    """
    self.string = ""
    if file:
      with open(file, "r") as f:
        self.string = f.read()
    self._modules = modules
    self._widgets = []

  def add_modules(self, *modules):
    """
    Add a module to be used.

    Parameters
    ----
    modules: list[str]
      module names.
    """
    self._modules.append(*modules)

  def generate(self, command):
    """
    Generate a Tk window based on the specified files and modules.

    Returns
    ----
    window: tkinter.Tk
      Tk window object.
    command: func
      An event handler for processing commands for widgets with the ::command element set.
    """
    def _generate_core(children, owner, modules):
      for i in children:
        cls = self._load_class(modules, i["classname"])
        obj, tag = self._instantiate(cls, callback=command, master=owner, **i["params"])
        if tag.hasdata(): self._widgets.append(tag)
        if i["children"]:
          _generate_core(i["children"], obj, modules)
    struct = yaml.safe_load(self.string)
    if not type(struct) is dict or len(struct) > 1:
      raise ValueError("The root node must be a dict and single.")
    modules = self._load_modules()
    tree = self._scantree(struct)
    cls  = self._load_class(modules, tree["classname"])
    root, tag = Generator._instantiate(cls, **tree["params"])
    if tag.hasdata(): self._widgets.append(tag)
    _generate_core(tree["children"], root, modules)
    return root

  def findbyid(self, id):
    """
    Search for widgets by ID.
    If multiple items with the same ID are defined, the first item is returned.

    Parameters
    ----
    id: str
      ID

    Returns
    ----
    widget: TagData|None
      If an item is found, TagData containing that widget.
      None if the item is not found.
    """
    l = list(filter(lambda x: x.id == id, self._widgets))
    return None if l == [] else l[0]

  def get_manager(self, commandhandler):
    """
    Create a window, store it in the `TkManager` that manages the window, and return it.

    Returns
    ----
    manager: TkManager
      A TkManager object that contains a window object.
    commandhandler: func
      An event handler for processing commands for widgets with the ::command element set.
    """
    window = self.generate(command=commandhandler)
    return TkManager(window, self._widgets)

  ### Private Methods

  def _load_modules(self):
    """
    Read all modules specified in the `self._modules` array
    and return the array.

    Returns
    ----
    modules: dict[str, module]
      A dictionary object that associates module names with module objects.

    Raises
    ----
    ModuleNotFoundError
      There is no module with the specified name.
    """
    modules = {}
    for mod in self._modules:
      modules[mod] = importlib.import_module(str(mod))
    return modules

  def _load_class(self, modules, class_name):
    """
    Search the class with the specified name and
    return the class object of the found class.

    Parameters
    ----
    modules: dict[str, module]
      A dictionary object that associates module names with module objects.
    class_name: str
      name of the class.
      If the class name contains ".", the left side of "."
      Is regarded as the module name and only the module with that name is searched.
      If the beginning of the character string is "_", it is ignored and processed.

    Returns
    ----
    class_object: class
      Class object.

    Raises
    ----
    TypeError
      If the specified class does not exist in the module specified by the argument.
      Or, if the specified class does not exist in the specified module.
    """
    mod = None
    cls = None
    if class_name[0] == "_":
      class_name = class_name[1:]
    if "." in class_name:
      # Module specified
      mod, cls = class_name.rsplit(".", 1)
    else:
      # Module search
      cls = class_name
      for module in modules.keys():
        cllist = map(lambda x: x[0], inspect.getmembers(modules[module], inspect.isclass))
        if cls in cllist:
          mod = module
          break

    if mod is None:
      raise TypeError("Class not found.")
    try:
      return getattr(modules[mod], cls)
    except AttributeError as e:
      raise TypeError(e)

  def _scantree(self, struct):
    """
    Scan an array and convert it to a tree of class names, parameters and child objects

    Parameters
    ----
    struct: dict
      Data array

    Retrns
    ----
    treedata: dict
      Tree data
    """
    def _scantree_core(struct, params):
      props = {
        "classname": "",
        "params": {},
        "children": [],
      }
      rootname = next(iter(struct))
      props["classname"] = rootname[1:]
      items = {}
      # merge params.
      if "params" in params:
        if struct[rootname] is None:
          items = params["params"]
        else:
          items = dict(params["params"], **struct[rootname])
      else:
        items = struct[rootname]
      # rootname check.
      if rootname == "::params":
        params["params"] = items
        return None
      # parse.
      for n, v in items.items():
        if n[0] == "_":
          props["children"].append(_scantree_core({n: v}, params))
        elif n == "::children":
          inparam = dict(params)
          for item in v:
            r = _scantree_core(item, inparam)
            if r is not None: props["children"].append(r)
        elif n == "::params":
          params["params"] = v
        else:
          if v is None:
            props["params"][n] = None
          else:
            props["params"][n] = v
      return props
    return _scantree_core(struct, {})

  @staticmethod
  def _get_argnames(method):
    """
    Get method argument list.
    If the document comment includes "STANDARD OPTIONS" and "WIDGET-SPECIFIC" OPTIONS,
    use that as the argument list.

    Parameters
    ----
    method: func
      Function object.

    Returns
    ----
    arglist: list(str)
      Argument list.
    """
    result = []
    # add inspect result
    for p in filter(lambda p: p.kind == p.POSITIONAL_OR_KEYWORD, inspect.signature(method).parameters.values()):
      result.append(p.name)

    # add comment args
    lines = method.__doc__.split("\n") if method.__doc__ else []
    i = 0
    collect = False
    while i < len(lines):
      if collect:
        if lines[i] == "":
          collect = False
        else:
          for p in lines[i].strip().split(","):
            if p != "": result.append(p.strip())
      else:
        if "STANDARD OPTIONS" in lines[i] or "WIDGET-SPECIFIC OPTIONS" in lines[i]:
          collect = True
          i += 1
      i += 1
    return result

  @staticmethod
  def _split_params(method, params):
    """
    Separate the parameter list into optional method arguments and anything else.

    Parameters
    ----
    method: func
      Method to be distributed.
    params: dict[str, any]
      Parameter list.

    Returns
    ----
    methodparams: dict[str, any]
      method arguments.
    other: dict[str, any]
      Any other value.
    """
    methodparams = {}
    for p in Generator._get_argnames(method):
      if p in params:
        methodparams[p] = params[p]
        del params[p]
    return methodparams, params

  @staticmethod
  def _instantiate(cls, callback=None, **params):
    """
    Generate an object with set properties based on class and property list.

    Parameters
    ----
    cls: class
      The object to instantiate.
    callback: func
      An event handler for processing commands for widgets with the ::command element set.
    params: dict(str, any)
      Property list.

    Returns
    ----
    instance: object
      The instantiated class.
    tagdata: TagData
      Widget additional data.
    """
    initparams, others = Generator._split_params(cls.__init__, params)
    obj = cls(**initparams)
    tagdata = TagData(obj)
    for n, v in others.items():
      if n.startswith("::"):
        if "id" in n:
          tagdata.id = v
        elif "tag" in n:
          tagdata.tag = v
        elif "command" in n and not callback is None:
          try:
            obj["command"] = EventReciever(obj, tagdata, callback)
          except tkinter.TclError:
            pass
      elif inspect.isroutine(getattr(obj, n)):
        attr = getattr(obj, n)
        attr() if v is None else attr(v)
      else:
        setattr(obj, n, v)
    return obj, tagdata

if __name__ == "__main__":
  gen = Generator()
  gen.string = """
  _Tk:
    title: "TEST Window"
    geometry: 400x300
    _Frame:
      pack:
      _Label:
        text: "Hello"
        pack:
  """
  window = gen.generate()
  window.mainloop()