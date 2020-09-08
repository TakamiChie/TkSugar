import unittest
import types
import tkinter

import yaml

from tksugar.generator import Generator

class ClassForTest(object):
  def __init__(self, a, b, c, d=1, e=2, f=3):
    self.a = a
    self.b = b
    self.c = c
    self.d = d
    self.e = e
    self.f = f
    self.g = None
    self.h = None
    self.i = False

  def g(self, value):
    self.g = value

  def h(self, value):
    self.h = value

  def i(self):
    self.i = True

  @staticmethod
  def j():
    """
    This method has documentation comments.
    STANDARD OPTIONS

    g, i,
    """
    pass

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

  #region test of _scantree()

  def test_scantree_simpledata(self):
    """
    When calling the `Generator#_scantree()` method under the following conditions,
    make sure that the method structures the tree.
    * Specify one Tk window in the file.
    """
    gen = Generator(modules=["tkinter"])
    with open("tests/definition/plane.yml", "r") as f:
      struct = yaml.safe_load(f)
      tree = gen._scantree(struct)
      self.assertEqual(tree["classname"], "Tk")
      self.assertEqual(len(tree["params"]), 1)
      self.assertEqual(tree["params"][0], ["title", "TEST Window"])
      self.assertEqual(len(tree["children"]), 0)

  def test_scantree_simpledata(self):
    """
    When calling the `Generator#_scantree()` method under the following conditions,
    make sure that the method structures the tree.
    * Specify one Tk window in the file.
    """
    gen = Generator(modules=["tkinter"])
    with open("tests/definition/plane.yml", "r") as f:
      struct = yaml.safe_load(f)
      tree = gen._scantree(struct)
      self.assertEqual(tree["classname"], "Tk")
      self.assertEqual(len(tree["params"]), 1)
      self.assertEqual(tree["params"][0], ["title", "TEST Window"])
      self.assertEqual(len(tree["children"]), 0)

  def test_scantree_button(self):
    """
    When calling the `Generator#_scantree()` method under the following conditions,
    make sure that the method structures the tree.
    * Specify one Tk window in the file.
    * There is a widget in the window.
    """
    gen = Generator(modules=["tkinter"])
    with open("tests/definition/button.yml", "r") as f:
      struct = yaml.safe_load(f)
      tree = gen._scantree(struct)
      self.assertEqual(tree["classname"], "Tk")
      self.assertEqual(tree["children"][0]["classname"], "Frame")
      self.assertEqual(tree["children"][0]["params"][0], ["grid"])
      self.assertEqual(tree["children"][0]["children"][0]["classname"], "Button")

  #endregion

  #region test of _get_argnames()

  def test_get_argnames(self):
    """
    When you call `Generator#get_argnames()` under the following conditions,
    Make sure to generate an argument list.
    * Common Python methods
    """
    list = Generator._get_argnames("".split)
    self.assertIn("maxsplit", list)

  def test_get_argnames_tkinterobj(self):
    """
    When you call `Generator#_get_argnames()` under the following conditions,
    make sure to add the contents of doc comment to the return value.
    * Target is tkinter module class __init__.
    """
    list = Generator._get_argnames(tkinter.Label.__init__)
    self.assertIn("activebackground", list)
    self.assertIn("text", list)
    self.assertIn("cnf", list)

  def test_get_argnames_hasnt_docstring(self):
    """
    When you call `Generator#get_argnames()` under the following conditions,
    Make sure to generate an argument list.
    * Document comment is not set in the method passed as an argument
    """
    list = Generator._get_argnames(ClassForTest.__init__)
    self.assertIn("a", list)
    self.assertIn("b", list)
    self.assertIn("c", list)

  def test_get_argnames_has_docstring(self):
    """
    When you call `Generator#get_argnames()` under the following conditions,
    Make sure to generate an argument list.
    * Document comment is set in the method passed as an argument
    """
    list = Generator._get_argnames(ClassForTest.j)
    self.assertListEqual(list, ["g", "i"])

  #endregion

  #region test of _split_params()

  def test_split_params(self):
    """
    When you call `Generator#_split_params()` under the following conditions,
    Confirm that the parameter list is returned correctly.
    * Target method parameters in the parameter list and other values ​​mixed.
    * All items in the parameter list have values.
    """
    params, others = Generator._split_params(tkinter.Label.__init__, {
      "text": "test",
      "bitmap": "abc",
      "test": "abc",
      "unknown": 123,
    })
    self.assertIn("text", params)
    self.assertIn("bitmap", params)
    self.assertIn("test", others)
    self.assertIn("unknown", others)

  def test_split_params_only_params(self):
    """
    When you call `Generator#_split_params()` under the following conditions,
    Confirm that the parameter list is returned correctly.
    * Only the parameter of the target method exists in the parameter list.
    * All items in the parameter list have values.
    """
    params, others = Generator._split_params(tkinter.Label.__init__, {
      "text": "test",
      "bitmap": "abc",
    })
    self.assertIn("text", params)
    self.assertIn("bitmap", params)
    self.assertEqual(len(others), 0)

  def test_split_params_only_others(self):
    """
    When you call `Generator#_split_params()` under the following conditions,
    Confirm that the parameter list is returned correctly.
    * Only the parameter of the target method exists in the parameter list.
    * All items in the parameter list have values.
    """
    params, others = Generator._split_params(tkinter.Label.__init__, {
      "test": "abc",
      "unknown": 123,
    })
    self.assertEqual(len(params), 0)
    self.assertIn("test", others)
    self.assertIn("unknown", others)

  def test_split_params_none_value(self):
    """
    When you call `Generator#_split_params()` under the following conditions,
    Confirm that the parameter list is returned correctly.
    * Target method parameters in the parameter list and other values ​​mixed.
    * Some of the items included in the parameter are None.
    """
    params, others = Generator._split_params(tkinter.Label.__init__, {
      "text": "test",
      "bitmap": None,
      "test": None,
      "unknown": 123,
    })
    self.assertIn("text", params)
    self.assertIn("bitmap", params)
    self.assertIn("test", others)
    self.assertIn("unknown", others)

  #endregion

if __name__ == "__main__":
  unittest.main()