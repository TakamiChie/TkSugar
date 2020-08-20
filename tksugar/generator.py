import importlib
import inspect
from typing import Type

import yaml

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

      Because modules can be added with the `addmodules()`,
      the value is specified here only if you do not want to load the tkinter module.
    """
    self.string = ""
    if file:
      with open(file, "r") as f:
        self.string = f.read()
    self._modules = modules

  def add_modules(self, *modules):
    """
    Add a module to be used.

    Parameters
    ----
    modules: list[str]
      module names.
    """
    self._modules.append(*modules)

  def generate(self):
    """
    Generate a Tk window based on the specified files and modules.

    Returns
    ----
    window: tkinter.Tk
      Tk window object.
    """
    def _generate_core(struct, owner, modules):
      for n, v in struct.items():
        if n[0] == "_":
          cls = self._load_class(modules, n)
          obj = cls(owner)
          _generate_core(v, obj, modules)
        else:
          attr = getattr(owner, n)
          if v is None:
            attr()
          else:
            attr(v)
    struct = yaml.safe_load(self.string)
    if not type(struct) is dict or len(struct) > 1:
      raise ValueError("The root node must be a dict and single.")
    modules = self._load_modules()
    rname = next(iter(struct))
    root = self._load_class(modules, rname)()
    _generate_core(struct[rname], root, modules)
    return root

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
    """
    def _scantree_core(struct):
      props = {
        "classname": "",
        "params": [],
        "children": [],
      }
      rootname = next(iter(struct))
      props["classname"] = rootname[1:]
      for n, v in struct[rootname].items():
        if n[0] == "_":
          props["children"].append(_scantree_core({n: v}))
        else:
          if v is None:
            props["params"].append([n])
          else:
            props["params"].append([n, v])
      return props
    return _scantree_core(struct)

if __name__ == "__main__":
  gen = Generator()
  gen.string = """
  - Tk
  """
  window = gen.generate()
  window.mainloop()