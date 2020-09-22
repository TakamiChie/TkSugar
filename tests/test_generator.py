import unittest
import tkinter

from tksugar.generator import Generator

class Test_Generator_Methods(unittest.TestCase):
  """
  Tests the `Generator#generate()` method.
  """

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

if __name__ == "__main__":
  unittest.main()