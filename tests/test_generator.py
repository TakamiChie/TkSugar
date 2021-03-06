import unittest
import tkinter
import yaml

from tksugar.generator import Generator

class Button(tkinter.Button):
  """
  We override the Button class for testing.
  """
  def __init__(self, master=None, cnf={}, **kw):
    """Construct a button widget with the parent MASTER.

    STANDARD OPTIONS

        activebackground, activeforeground, anchor,
        background, bitmap, borderwidth, cursor,
        disabledforeground, font, foreground
        highlightbackground, highlightcolor,
        highlightthickness, image, justify,
        padx, pady, relief, repeatdelay,
        repeatinterval, takefocus, text,
        textvariable, underline, wraplength

    WIDGET-SPECIFIC OPTIONS

        command, compound, default, height,
        overrelief, state, width
    """
    tkinter.Button.__init__(self, **kw)
    self.items = []
    self.testdict = {}

  def items(self, items):
    self.items.append(items)

class Test_Generator(unittest.TestCase):
  """
  Tests the `Generator#generate()` method.
  """

  def tearDown(self):
    tkinter._default_root = None

  #region Test of normal operation.

  def test_plane(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Specify one Tk window in the file.
    """
    gen = Generator("tests/definition/generator_test/plane.yml")
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
    gen = Generator("tests/definition/generator_test/button.yml")
    tk = gen.generate()
    self.assertEquals(type(tk.children["!frame"]), tkinter.Frame)
    self.assertEquals(type(tk.children["!frame"].children["!button"]), tkinter.Button)

  def test_localize(self):
    """
    When you call the `Generator#generate()` method with the following conditions
    Verify that the translation is done.
    * Specify one Tk window in the file.
    * Specify existing translation dictionary files.
    """
    gen = Generator("tests/definition/generator_test/localize_target.yml", localization_file="tests/definition/generator_test/localize_script.yml")
    gen.generate()
    self.assertEquals(gen.findbyid("button").widget.cget("text"), "translated")

  def test_idtags(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Specify one Tk window in the file.
    * There is a widget in the window.
    * ID and tag elements are defined in windows and widgets.
    """
    gen = Generator("tests/definition/generator_test/idtags.yml")
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
    gen = Generator("tests/definition/generator_test/variable.yml")
    tk = gen.generate()
    self.assertIsNotNone(type(gen.findbyid("test1").widget["textvariable"]))
    self.assertIsNotNone(type(gen.findbyid("test2").widget["textvariable"]))
    self.assertIsNotNone(type(gen.findbyid("test3").widget["textvariable"]))
    self.assertIsNotNone(type(gen.findbyid("test4").widget["textvariable"]))
    self.assertIs(type(gen.vars["test1"]), tkinter.StringVar)

  def test_variable_in_array(self):
    """
    When the `Generator#generate()` method is called with the following conditions
    Make sure that all variable objects set in the parameters are expanded.
    * A var variable exists on a node other than the node directly under the widget.
    """
    gen = Generator(file="tests/definition/generator_test/variable_in_array.yml", modules=["tests.test_generator", "tkinter"])
    gen.generate()
    self.assertIs(type(gen.findbyid("button1").widget.items[0]), tkinter.IntVar)
    self.assertIs(type(gen.findbyid("button2").widget.testdict["testvar"]), tkinter.StringVar)

  def test_include(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Include another YAML file within a YAML file.
    """
    gen = Generator("tests/definition/generator_test/multiple_files.yml")
    tk = gen.generate()
    self.assertEquals(type(gen.findbyid("testbutton").widget), tkinter.Button)

  def test_widget_override(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Multiple modules are referenced.
    * Overriding an existing tkinter widget in the referenced module.
    """
    gen = Generator(file="tests/definition/generator_test/button.yml", modules=["tests.test_generator", "tkinter"])
    tk = gen.generate()
    self.assertEquals(gen.findbyid("test").widget.__class__.__module__, "tests.test_generator")

  def test_load_utf8(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Contains Japanese characters.
    * The encoding of the file is UTF-8.
    """
    gen = Generator("tests/definition/generator_test/japanese_utf8.yml")
    gen.generate()
    self.assertEquals(gen.findbyid("test").widget.cget("text"), "ボタン")

  def test_load_sjis(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Contains Japanese characters.
    * The encoding of the file is Shift-JIS.
    * Specify Shift-JIS as the encoding in the Generator argument.
    """
    gen = Generator("tests/definition/generator_test/japanese_sjis.yml", encoding="Shift_JIS")
    gen.generate()
    self.assertEquals(gen.findbyid("test").widget.cget("text"), "ボタン")

  #endregion

  #region Test of semi-normal operation

  def test_include_multidir(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * Include another YAML file within a YAML file.
    * The file path of the YAML file read the first time and the YAML file read the second time are different.
    """
    Generator("tests/definition/generator_test/multiple_files.yml")
    gen = Generator("tests/definition/generator_test/testdir/multiple_files.yml")
    tk = gen.generate()
    self.assertEquals(type(gen.findbyid("testbutton").widget), tkinter.Button)

  def test_no_localize(self):
    """
    When you call the `Generator#generate()` method with the following conditions
    Verify that no translation is done.
    * Specify one Tk window in the file.
    * Do not specify the translation dictionary file.
    """
    gen = Generator("tests/definition/generator_test/localize_target.yml")
    gen.generate()
    self.assertEquals(gen.findbyid("button").widget.cget("text"), "OK")

  def test_command_no_handler(self):
    """
    Confirm that the target Tk window is created when the `Generator#generate()` method
    is called under the following conditions.
    * There is a widget in the YAML file that contains the `::command` keyword
    * Argument command of `Generator#generate()` is not specified
    """
    gen = Generator("tests/definition/generator_test/has_command.yml")
    tk = gen.generate()
    self.assertTrue(True)

  #endregion

  #region Abnormal behavior test

  def test_variable_noname(self):
    """
    Confirm that ValueError occurs when calling the `Generator#generate()` method under the following conditions.
    * Specify one Tk window in the file.
    * The widget variable does not contain a name.
    """
    gen = Generator("tests/definition/generator_test/variable_error2.yml")
    with self.assertRaises(ValueError):
      gen.generate()

  def test_variable_no_variable(self):
    """
    Confirm that ValueError occurs when calling the `Generator#generate()` method under the following conditions.
    * Specify one Tk window in the file.
    * Specify the class name of a class that is not a subclass of Variable as the widget variable type.
    """
    gen = Generator("tests/definition/generator_test/variable_error3.yml")
    with self.assertRaises(ValueError):
      gen.generate()

  def test_variable_unknown_name(self):
    """
    Confirm that AttributeError occurs when calling the `Generator#generate()` method under the following conditions.
    * Specify one Tk window in the file.
    * The widget variable type is a non-existent class name.
    """
    gen = Generator("tests/definition/generator_test/variable_error4.yml")
    with self.assertRaises(AttributeError):
      gen.generate()

  def test_unkown_keyword(self):
    """
    Confirm that NameError occurs when calling the `Generator#generate()` method under the following conditions.
    * Specify one Tk window in the file.
    * Keyword is a non-existent name.
    """
    gen = Generator("tests/definition/generator_test/command_unknown.yml")
    with self.assertRaises(NameError):
      gen.generate()

  def test_load_sjis_noencode(self):
    """
    Confirm that UnicodeDecodeError occurs when calling the `Generator#generate()` method under the following conditions.
    * Contains Japanese characters.
    * The encoding of the file is Shift-JIS.
    * Do not specify the encoding in the Generator argument.
    """
    with self.assertRaises(UnicodeDecodeError):
      Generator("tests/definition/generator_test/japanese_sjis.yml")

  #endregion

if __name__ == "__main__":
  unittest.main()