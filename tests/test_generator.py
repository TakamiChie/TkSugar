import unittest
import tkinter
import yaml

from tksugar.generator import Generator

class Test_Generator_Methods(unittest.TestCase):
  """
  Tests the `Generator#generate()` method.
  """

  def setUp(self):
    if tkinter._default_root:
      tkinter._default_root.destroy()

  #region Test of normal operation.

  def test_plane(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Specify one Tk window in the file.
    """
    gen = Generator("tests/definition/plane.yml")
    tk = gen.generate()
    self.assertEquals(type(tk), tkinter.Tk)
    self.assertEquals(tk.title(), "TEST Window")

  def test_button(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Specify one Tk window in the file.
    * There is a widget in the window.
    """
    gen = Generator("tests/definition/button.yml")
    tk = gen.generate()
    self.assertEquals(type(tk.children["!frame"]), tkinter.Frame)
    self.assertEquals(type(tk.children["!frame"].children["!button"]), tkinter.Button)

  def test_idtags(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Specify one Tk window in the file.
    * There is a widget in the window.
    * ID and tag elements are defined in windows and widgets.
    """
    gen = Generator("tests/definition/idtags.yml")
    tk = gen.generate()
    self.assertEquals(type(gen.findbyid("test").widget), tkinter.Tk)
    self.assertEquals(type(gen.findbyid("testbutton").widget), tkinter.Button)
    self.assertIsNone(gen.findbyid("unknown"))

  def test_variable(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Specify one Tk window in the file.
    * There is a widget in the window.
    * Widget variables are set in the widget.
    """
    gen = Generator("tests/definition/variable.yml")
    tk = gen.generate()
    self.assertIsNotNone(type(gen.findbyid("test1").widget["textvariable"]))
    self.assertIsNotNone(type(gen.findbyid("test2").widget["textvariable"]))
    self.assertIsNotNone(type(gen.findbyid("test3").widget["textvariable"]))
    self.assertIsNotNone(type(gen.findbyid("test4").widget["textvariable"]))
    self.assertIs(type(gen.vars["test1"]), tkinter.StringVar)

  def test_include(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Include another YAML file within a YAML file.
    """
    gen = Generator("tests/definition/multiple_files.yml")
    tk = gen.generate()
    self.assertEquals(type(gen.findbyid("testbutton").widget), tkinter.Button)

  def test_multinode(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Read a YAML file consisting of multiple nodes.
    * The top-level node in the YAML file is the list.
    * After reading the YAML file consisting of a single node.
    """
    Generator("tests/definition/plane.yml").generate()
    gen = Generator("tests/definition/multinode.yml")
    widgets = gen.generate()
    self.assertEquals(len(widgets), 3)

  def test_multinode_hash(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Read a YAML file consisting of multiple nodes.
    * The top-level node in the YAML file is the dict.
    * After reading the YAML file consisting of a single node.
    """
    Generator("tests/definition/plane.yml").generate()
    gen = Generator("tests/definition/multinode_hash.yml")
    widgets = gen.generate()
    self.assertIs(type(widgets[0]), tkinter.Button)
    self.assertIs(type(widgets[1]), tkinter.Label)

  #endregion

  #region Test of semi-normal operation

  def test_include_multidir(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Include another YAML file within a YAML file.
    * The file path of the YAML file read the first time and the YAML file read the second time are different.
    """
    Generator("tests/definition/multiple_files.yml")
    gen = Generator("tests/definition/testdir/multiple_files.yml")
    tk = gen.generate()
    self.assertEquals(type(gen.findbyid("testbutton").widget), tkinter.Button)

  #endregion

  #region Abnormal behavior test

  def test_variable_toplevel_window(self):
    """
    Confirm that ValueError occurs when calling the `Generator#generate()` method under the following conditions.
    * Specify one Tk window in the file.
    * Widget variables are set in the top level window.
    """
    gen = Generator("tests/definition/variable_error.yml")
    with self.assertRaises(ValueError):
      gen.generate()

  def test_variable_noname(self):
    """
    Confirm that ValueError occurs when calling the `Generator#generate()` method under the following conditions.
    * Specify one Tk window in the file.
    * The widget variable does not contain a name.
    """
    gen = Generator("tests/definition/variable_error2.yml")
    with self.assertRaises(ValueError):
      gen.generate()

  def test_variable_no_variable(self):
    """
    Confirm that ValueError occurs when calling the `Generator#generate()` method under the following conditions.
    * Specify one Tk window in the file.
    * Specify the class name of a class that is not a subclass of Variable as the widget variable type.
    """
    gen = Generator("tests/definition/variable_error3.yml")
    with self.assertRaises(ValueError):
      gen.generate()

  def test_variable_unknown_name(self):
    """
    Confirm that AttributeError occurs when calling the `Generator#generate()` method under the following conditions.
    * Specify one Tk window in the file.
    * The widget variable type is a non-existent class name.
    """
    gen = Generator("tests/definition/variable_error4.yml")
    with self.assertRaises(AttributeError):
      gen.generate()

  def test_multinode_valueerror(self):
    """
    Confirm that ValueError occurs when calling the `Generator#generate()` method under the following conditions.
    * Read a YAML file consisting of multiple nodes.
    * Generator is not reading a YAML file consisting of a single node.
    """
    gen = Generator("tests/definition/multinode.yml")
    with self.assertRaises(ValueError):
      gen.generate()

  def test_multinode_node_valueerror(self):
    """
    Confirm that ValueError occurs when calling the `Generator#generate()` method under the following conditions.
    * Read a YAML file consisting of multiple nodes.
    * The top-level node of the YAML file is neither dict nor list.
    * Read a YAML file consisting of multiple nodes.
    * After reading the YAML file consisting of a single node.
    """
    Generator("tests/definition/plane.yml").generate()
    gen = Generator("tests/definition/multinode_value.yml")
    with self.assertRaises(ValueError):
      gen.generate()

  #endregion

if __name__ == "__main__":
  unittest.main()