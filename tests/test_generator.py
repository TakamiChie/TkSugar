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

if __name__ == "__main__":
  unittest.main()