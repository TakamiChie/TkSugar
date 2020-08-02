import unittest
import types

from tksugar.generator import Generator

class Test_Generator_Methods(unittest.TestCase):
  """
  Method tests other than the `generate()` method of the Generator class.
  """

  #region test of add_module()

  def test_add_module(self):
    """
    Confirm that the module added by `Generator#add_modules()`
    is treated the same as the module added by the constructor.
    """
    gen = Generator(modules=["tkinter"])
    gen.add_modules("tkinter.ttk")
    mods = gen._load_modules()
    self.assertEquals(len(mods), 2)
    self.assertEquals(type(mods["tkinter"]), types.ModuleType)
    self.assertEquals(type(mods["tkinter.ttk"]), types.ModuleType)

  #endregion

  #region test of _load_module()
  def test_load_module_empty(self):
    """
    Confirm that an empty array is returned when `Generator#_load_modules()` is
    called under the following conditions.
    * The number of modules specified in the _modules array is 0
    """
    gen = Generator(modules=[])
    mods = gen._load_modules()
    self.assertEquals(len(mods), 0)

  def test_load_module_module_not_found(self):
    """
    Confirm that ModuleNotFoundError is thrown
    when `Generator#_load_modules()` is called under the following conditions.
    * The module with the specified name does not exist.
    """
    gen = Generator(modules=["unknown_module"])
    with self.assertRaises(ModuleNotFoundError):
      gen._load_modules()

  def test_load_module_module_not_found_at_once(self):
    """
    Confirm that ModuleNotFoundError is thrown
    when `Generator#_load_modules()` is called under the following conditions.
    * Modules that exist and modules that do not exist are mixed in the module name array.
    """
    gen = Generator(modules=["tkinter", "unknown_module"])
    with self.assertRaises(ModuleNotFoundError):
      gen._load_modules()

  def test_load_module_empty_string(self):
    """
    Confirm that ValueError is thrown
    when `Generator#_load_modules()` is called under the following conditions.
    * The array contains an empty string.
    """
    gen = Generator(modules=[""])
    with self.assertRaises(ValueError):
      gen._load_modules()

  def test_load_module_simple(self):
    """
    Make sure that `Generator#_load_modules()` loads all modules under the following conditions.
    * Only one module specified in the argument.
    """
    gen = Generator(modules=["tkinter"])
    mods = gen._load_modules()
    self.assertEquals(len(mods), 1)
    self.assertEquals(next(iter(mods)), "tkinter")

  def test_load_module_multiple_items(self):
    """
    Make sure that `Generator#_load_modules()` loads all modules under the following conditions.
    * Multiple module names are specified in the argument.
    """
    gen = Generator(modules=["tkinter", "tkinter.ttk"])
    mods = gen._load_modules()
    self.assertEquals(len(mods), 2)
    self.assertEquals(type(mods["tkinter"]), types.ModuleType)
    self.assertEquals(type(mods["tkinter.ttk"]), types.ModuleType)

  #endregion

  #region test of _load_class()

  def test_load_class_anymodule_oneclass(self):
    """
    Confirm that the class is searched
    when `Generator#_load_class()` is called under the following conditions.
    * No module name specified.
    * The class exists in the loaded module list.
    """
    gen = Generator(modules=["tkinter", "tkinter.ttk"])
    mods = gen._load_modules()
    cls = gen._load_class(mods, "Notebook")
    self.assertEquals(type(cls), type)

  def test_load_class_onemodule_oneclass(self):
    """
    Confirm that the class is searched
    when `Generator#_load_class()` is called under the following conditions.
    * Module name is specified.
    * The class exists in the loaded module list.
    """
    gen = Generator(modules=["tkinter", "tkinter.ttk"])
    mods = gen._load_modules()
    cls = gen._load_class(mods, "tkinter.ttk.Notebook")
    self.assertEquals(type(cls), type)

  def test_load_class_underscore(self):
    """
    Confirm that the class is searched
    when `Generator#_load_class()` is called under the following conditions.
    * There is an underscore before the module name.
    """
    gen = Generator(modules=["tkinter", "tkinter.ttk"])
    mods = gen._load_modules()
    cls = gen._load_class(mods, "_Notebook")
    self.assertEquals(type(cls), type)

  def test_load_class_unmatched_anymodule_oneclass(self):
    """
    Confirm that a TypeError occurs when calling `Generator#_load_class()`
    under the following conditions.
    * No module name specified.
    * Class does not exist in the loaded module list.
    """
    gen = Generator(modules=["tkinter", "tkinter.ttk"])
    mods = gen._load_modules()
    with self.assertRaises(TypeError):
      gen._load_class(mods, "UnknownType")

  def test_load_class_unmatched_onemodule_oneclass(self):
    """
    Confirm that a TypeError occurs when calling `Generator#_load_class()`
    under the following conditions.
    * Module name is specified.
    * Class does not exist in the loaded module list.
    """
    gen = Generator(modules=["tkinter", "tkinter.ttk"])
    mods = gen._load_modules()
    with self.assertRaises(TypeError):
      gen._load_class(mods, "tkinter.UnknownType")

  def test_load_class_different_module_onemodule_oneclass(self):
    """
    Confirm that a TypeError occurs when calling `Generator#_load_class()`
    under the following conditions.
    * Module name is specified.
    * The class exists in the loaded module list but does not exist in the specified module.
    """
    gen = Generator(modules=["tkinter", "tkinter.ttk"])
    mods = gen._load_modules()
    with self.assertRaises(TypeError):
      gen._load_class(mods, "tkinter.Notebook")

  #endregion

if __name__ == "__main__":
  unittest.main()