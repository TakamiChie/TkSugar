import importlib
import inspect
from pathlib import Path
import tkinter
import re
from typing import Type

import yaml
from yamlinclude import YamlIncludeConstructor

from tksugar.tkmanager import TkManager
from tksugar.localizer import Localizer
from tksugar.widgets.generatorsupport import GeneratorSupport
from tksugar.eventreciever import EventReciever

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
    self.callback = None

  def hasdata(self):
    """
    True if there is data.

    Returns
    ----
    hasdata: bool
      True if there is data
    """
    return self.id or self.tag

  def performclick(self):
    """
    If the button has a command, execute it.
    """
    if self.callback is not None:
      self.callback(self.widget, self)

class TemporaryVariable(object):
  """
  A temporary variable object that indicates where to replace the tkinter.Variable object.
  Hold only the variable name.
  """
  def __init__(self, name):
    self.name = name

class GeneratorLoader(yaml.SafeLoader):
  """
  YAML Loader used in Generator.
  A custom tag reading process is added.
  """
  def __init__(self, stream):
    super().__init__(stream)
    self.vars = {}
    yaml.add_multi_constructor("tag:yaml.org,2002:var", GeneratorLoader.var_handler,
      Loader=GeneratorLoader)

  @staticmethod
  def var_handler(loader, suffix, node=None):
    """
    A handler that responds to variable definitions.
    """
    if suffix[0] == ":": suffix = suffix[1:]
    name = ""
    default = None
    for v in node.value:
      if v[0].value == "name": name = v[1].value
      if v[0].value == "default": default = v[1].value
    if name != "":
      var = getattr(tkinter, suffix)
      if not issubclass(var, tkinter.Variable): raise ValueError("The specified class is not a Variable class.")
      loader.vars[name] = {"class": var, "default": default}
      return TemporaryVariable(name)
    else:
      raise ValueError("The variable name is not set.")

#region command classes

class CommandBaseClass(object):
  """
  A base class that defines the content of commands in YAML files.
  """
  def __init__(self, postactions):
    """
    constuructor

    Parameters
    ----
    postactions: list
      If there is a method you want to call after creating the object list, add it to this list.
    """
    self.postactions = postactions

  def __call__(self, obj, tag, value):
    self.command(obj, tag, value)

  def command(self, obj, tag, value):
    """
    Command executor

    Parameters
    ----
    obj: object
      The associated object.
    tag: Any
      Tag object.
    value: Any
      The value defined in the YAML file.
    """
    raise NotImplementedError

class IdCommand(CommandBaseClass):
  """
  A command that associates an object with an internal ID.
  """
  def command(self, object, tag, value):
    tag.id = str(value)

class TagCommand(CommandBaseClass):
  """
  A command that associates an object with tag data.
  """
  def command(self, object, tag, value):
    tag.tag = value

class CommandCommand(CommandBaseClass):
  """
  A command that associates a callback method that responds to an object's command.
  """
  def __init__(self, postactions, callback):
    """
    Constructor

    Parameters
    ----
    callback: func
      An event handler for processing commands for widgets with the ::command element set.
    """
    super().__init__(postactions)
    self.callback = callback

  def command(self, object, tag, value):
    try:
      if not self.callback is None:
        resv = EventReciever(object, tag, self.callback)
        if "command" in dir(object):
          setattr(object, "command", resv)
        else:
          object["command"] = resv
    except tkinter.TclError:
      pass

class GridColumnCommand(CommandBaseClass):
  """
  Configure columns on the grid.

  Parameters at Commands
  ----
  index: int
    Column index.
  minsize: int
    Specify the minimum width / height numerically.
  weight: int
    Specify the ratio when allocating the margin numerically.
  pad: int
    Specify the padding numerically.
  """

  def command(self, object, tag, value):
    def _command():
      indx = value["index"]
      del value["index"]
      object.grid_columnconfigure(indx, value)

    self.postactions.append(_command)

class GridRowCommand(CommandBaseClass):
  """
  Configure columns on the grid.

  Parameters at Commands
  ----
  index: int
    Row index.
  minsize: int
    Specify the minimum width / height numerically.
  weight: int
    Specify the ratio when allocating the margin numerically.
  pad: int
    Specify the padding numerically.
  """

  def command(self, object, tag, value):
    def _command():
      indx = value["index"]
      del value["index"]
      object.grid_rowconfigure(indx, value)

    self.postactions.append(_command)

#endregion

class Generator(object):
  """
  The core object that creates the Tk window.
  Users of this module will use this core object to generate a Tk window.
  """
  def __init__(self, file="",modules=["tksugar.widgets", "tkinter"], localization_file="", encoding="UTF-8"):
    """
    constructor.

    Parameters
    ----
    file: str
      A file path describing the window's object and layout.
      This argument can be omitted, but in actual use it is not omitted in principle.
      Omitted only when testing.
      If you omit the file name, YamlIncludeConstructor will not be deleted, so YAML's `!Include` will remain valid.
      However, this operation is not dealt with because it is impossible in principle to omit the file in the first place and there is no actual harm.
    modules: list[str]
      An array indicating the name of the module to be used.
      By default, it is "tkinter" only.

      Because modules can be added with the `Generator#add_modules()`,
      the value is specified here only if you do not want to load the tkinter module.
    localization_file: str
      Path indicating a YAML-formatted dictionary file used for UI localization.
      This dictionary contains only dict, list, and str.
      If the format is wrong, no error is generated at this point, even if the path does not exist.

      If omitted, the UI localizer is disabled.
    encoding: str
      File Encoding.
    """
    self.string = ""
    if file:
      with open(file, "r", encoding=encoding) as f:
        self.string = f.read()
      YamlIncludeConstructor.add_to_loader_class(loader_class=GeneratorLoader, base_dir=str(Path(file).parent))
    self._modules = modules
    self._widgets = []
    self.localization_file = localization_file
    self.localization_file_encoding = encoding
    self.vars = None

  def add_modules(self, *modules):
    """
    Add a module to be used.

    Parameters
    ----
    modules: list[str]
      module names.
    """
    self._modules.append(*modules)

  def generate(self, command=None):
    """
    Generate a Tk window based on the specified files and modules.

    Parameters
    ----
    command: func
      An event handler for processing commands for widgets with the ::command element set.

    Returns
    ----
    window: tkinter.Tk
      Tk window object.
    """
    def _generate_core(children, owner, modules):
      for i in children:
        cls = self._load_class(modules, i["classname"])
        objparam = i["params"]
        if not issubclass(type(owner), GeneratorSupport):
          # GenetratorSupport non inherited class, which adds a master parameter and adds a child object.
          objparam["master"] = owner
        obj, tag = self._instantiate(cls, callback=command, **objparam)
        if issubclass(type(owner), GeneratorSupport):
          # GeneratorSupport inherited class, which adds a child object via append_child.
          childparam = {}
          for n, v in objparam.items():
            if n.startswith("/"):
              childparam[n[1:]] = v
          owner.append_child(obj, **childparam)
        if tag.hasdata(): self._widgets.append(tag)
        if i["children"]:
          _generate_core(i["children"], obj, modules)
    # Load YAML
    loader = GeneratorLoader(self.string)
    try:
      struct = loader.get_single_data()
    finally:
      loader.dispose()
    self.vars = loader.vars
    if not type(struct) is dict or len(struct) > 1:
      raise ValueError("The root node must be a dict and single.")
    # Prepare
    l = Localizer(self.localization_file, self.localization_file_encoding)
    l.localize(struct)
    modules = self._load_modules()
    tree = self._scantree(struct)
    # Load Root Object
    cls  = self._load_class(modules, tree["classname"])
    root, tag = self._instantiate(cls, callback=command, **tree["params"])
    if tag.hasdata(): self._widgets.append(tag)
    # Load Variable
    for n, v in self.vars.items():
      self.vars[n] = v["class"](master=root, name=n)
      if not v["default"] is None:
        self.vars[n].set(v["default"])
    # Load Child Object
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

  def get_manager(self, commandhandler=None):
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
    return TkManager(window, self._widgets, self.vars)

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

  @staticmethod
  def _load_class(modules, class_name):
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
        cllist = list(map(lambda x: x[0], inspect.getmembers(modules[module], inspect.isclass)))
        if cls in cllist:
          mod = module
          break

    if mod is None:
      raise TypeError(f'Class not found. "{class_name}"')
    try:
      return getattr(modules[mod], cls)
    except AttributeError as e:
      raise TypeError(e)

  @staticmethod
  def _scantree(struct):
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
        if items is None:
          raise ValueError(f'Missing value or element in node name "{rootname}". Is the indentation level wrong?')
      # rootname check.
      if rootname == "::params":
        params["params"] = items
        return None
      # parse.
      for n, v in items.items():
        if n[0] == "_":
          props["children"].append(_scantree_core({n: v}, params))
        elif n == "::children":
          if type(v) is not list:
            raise AttributeError("The child elements of the ::children node must be an list.")
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
          for p in filter(lambda x: x, re.split("[\s,]", lines[i].strip())):
            result.append(p.strip())
      else:
        if "STANDARD OPTIONS" in lines[i] or "WIDGET-SPECIFIC OPTIONS" in lines[i]:
          collect = True
          i += 1
        if "Valid resource names:" in lines[i]:
          collect = True
          lines[i] = lines[i].split(":")[1]
          i -= 1
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

  def _instantiate(self, cls, callback=None, **params):
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
    def replace_variable(params):
      """
      Recursively replaces the TemporaryVariable class present in all parameters.
      """
      for n in params.keys() if type(params) is dict else range(len(params)):
        if type(params[n]) is TemporaryVariable:
          params[n] = self.vars[params[n].name]
        elif type(params[n]) is list or type(params[n]) is dict:
          replace_variable(params[n])
    # Prepare
    replace_variable(params)
    initparams, others = Generator._split_params(cls.__init__, params)
    postactions = []
    commands = {
      "id": IdCommand(postactions),
      "tag": TagCommand(postactions),
      "gridcolumn": GridColumnCommand(postactions),
      "gridrow": GridRowCommand(postactions),
    }
    commands["command"] = CommandCommand(postactions, callback)
    # Instantiation
    obj = cls(**initparams)
    tagdata = TagData(obj)
    if callback is not None:
      tagdata.callback = callback
    # Other property settings
    for n, v in others.items():
      if n.startswith("::"):
        if n[2:] in commands:
          commands[n[2:]](obj, tagdata, v)
        else:
          raise NameError("Command Not Found('{0}')".format(n[2:]))
      elif n.startswith("/"):
        pass
      elif inspect.isroutine(getattr(obj, n)):
        attr = getattr(obj, n)
        attr() if v is None else attr(v)
      else:
        setattr(obj, n, v)
    # Post actions
    for fun in postactions:
      fun()
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