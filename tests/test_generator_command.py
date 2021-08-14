import tkinter
import unittest
from typing import Callable, List

import pyautogui

from tksugar import Generator, TkManager

class TestFrame(tkinter.Frame):

  class CommandButton(object):
    def __init__(self, owner):
      self.owner = owner

    def __call__(self):
      self.owner._buttonpressed()

  def __init__(self, master=None, cnf={}, **kw):
    """
    constructor

    STANDARD OPTIONS

    textvariable
    """
    tkinter.Frame.__init__(self, master, cnf)
    self._command = None
    self.grid()
    self.textbox = tkinter.Entry(self, kw)
    self.textbox.grid(row=0, column=0, sticky="ew", padx=4, ipadx=2, ipady=2)
    self.button = tkinter.Button(self, text="Test", command=self.CommandButton(self))
    self.button.grid(row=0, column=1, ipadx=2, ipady=2)

  def _buttonpressed(self):
    """
    Event handler that will be called when the button is clicked.
    """
    self.command()

  @property
  def command(self):
    """
    Gets or sets an event handler that will be executed when the button is pressed.
    """
    return self._command

  @command.setter
  def command(self, value):
    """
    Gets or sets an event handler that will be executed when the button is pressed.
    """
    self._command = value

class Test_Generator_command(unittest.TestCase):
  """
  Testing the `command` parameter of the`Generator#generate()` method.
  """

  def setUp(self) -> None:
    self.success = False
    self.exceptions = None
    return super().setUp()

  def tearDown(self):
    tkinter._default_root = None

  def passed(self):
    """
    Mark the test item success.
    Marks are removed at the beginning of the next test.

    In the test method, the value to be set can be changed by adding the value of `#success` before calling the `#passed()` method for the first time.
    number:`#passed()` The value is added to each time the method calls.
    array:`#passed()`True is added to the array each time the method is called.
    """
    if type(self.success) is int:
      self.success += 1;
    elif type(self.success) is list:
      self.success.append(True)
    else:
      self.success = True

  def do_test(self, file: str, test: Callable[[TkManager], None], command: Callable= None,
    modules: List[str] = []):
    """
    Display the GUI screen for testing.
    This method executes each test code after 100 milliseconds of GUI display.

    Parameters
    ----
    file: str
      YAML file that defines the GUI for testing.
    test: Callable[TkManager] -> None
      Test code, where the method is called 100 milliseconds after the GUI window is displayed.
      The TkManager generated by the generator is stored in the argument.
    command: Callable[] -> None
      Callback method to be called when the command is executed. None when omitted。
    modules: List
      Module to be read.If specified, the standard module list is overwritten.
    """
    def _do():
      if test is not None:
        man.window.focus_force()
        try:
          test(man)
        except Exception as e:
          self.exceptions = e
        man.window.after(500, lambda : man.window.destroy())
    man = Generator(file=file,
      modules=["tksugar.widgets", "tkinter"] if modules == [] else modules) \
      .get_manager(commandhandler=command)
    man.window.after(100, _do)
    man.mainloop()
    if self.exceptions is not None:
      raise self.exceptions
    return man

  def test_button(self):
    """
    When the method is executed with the `command` parameter specified in `Generator#generator()` under the following conditions
    Confirm that the handler specified in `command` is executed.
    """
    def test(man: TkManager):
      pyautogui.press("tab")
      pyautogui.press("space")
    def command(obj, tag):
      self.passed()
    self.do_test("tests/definition/command_test/call_command.yml", command=command, test=test)
    self.assertTrue(self.success, "Command was not executed.")

  def test_button_multiple(self):
    """
    When the method is executed with the `command` parameter specified in `Generator#generator()` under the following conditions
    Confirm that the handler specified in `command` is executed.
    * Multiple buttons.
    """
    def test(man: TkManager):
      for i in range(3):
        pyautogui.press("tab")
        pyautogui.press("space")
    def command(obj, tag):
      if (self.success + 1) == obj["text"]: self.passed()
    self.success = 0;
    self.do_test("tests/definition/command_test/call_command_multiple.yml", command=command, test=test)
    self.assertEqual(self.success, 3, "Command was not executed.")

  def test_customwidget(self):
    """
    When the method is executed with the `command` parameter specified in `Generator#generator()` under the following conditions
    Confirm that the handler specified in `command` is executed.
    * CustomWidget
    """
    def test(man: TkManager):
      pyautogui.press("tab")
      for i in range(5):
        pyautogui.press(f"{i}")
      pyautogui.press("tab")
      pyautogui.press("space")
    def command(obj, tag):
      self.passed()
    man = self.do_test("tests/definition/command_test/call_customwidget.yml", command=command,
      test=test,
      modules=["tkinter", "tests.test_generator_command"])
    self.assertTrue(self.success, "Command was not executed.")
    self.assertEqual(man.vars["test"].get(), "01234", "An input value reflection test.")

  def test_menu(self):
    """
    When the method is executed with the `command` parameter specified in `Generator#generator()` under the following conditions
    Confirm that the handler specified in `command` is executed.
    * Menu
    """
    def test(man: TkManager):
      for i in range(3):
        pyautogui.press(["alt", f"{i + 1}"])
        pyautogui.press("enter")
    def command(obj, tag):
      if f"{(self.success + 1)}" == tag.tag["item"]: self.passed()
    self.success = 0
    self.do_test("tests/definition/command_test/call_menu.yml", command=command,
      test=test)
    self.assertEqual(self.success, 3, "Command was not executed.")

  def test_multifile(self):
    """
    When the method is executed with the `command` parameter specified in `Generator#generator()` under the following conditions
    Confirm that the handler specified in `command` is executed.
    * Use multiple YAML files for GUI definitions.
    """
    def test(man: TkManager):
      pyautogui.press("tab")
      pyautogui.press("space")
    def command(obj, tag):
      self.passed()
    self.do_test("tests/definition/command_test/call_multifile_main.yml", command=command, test=test)
    self.assertTrue(self.success, "Command was not executed.")

  def test_notebook(self):
    """
    When the method is executed with the `command` parameter specified in `Generator#generator()` under the following conditions
    Confirm that the handler specified in `command` is executed.
    * Using Notebook
    """
    def test(man: TkManager):
      pyautogui.press("tab")
      pyautogui.press("tab")
      pyautogui.press("space")
    def command(obj, tag):
      self.passed()
    self.do_test("tests/definition/command_test/call_notebook.yml", command=command, test=test)
    self.assertTrue(self.success, "Command was not executed.")

  def test_notebook_not_root(self):
    """
    When the method is executed with the `command` parameter specified in `Generator#generator()` under the following conditions
    Confirm that the handler specified in `command` is executed.
    * Using Notebook
    * The window that owns the Notebook is not the DefaultRoot.
    """
    def test(man: TkManager):
      pyautogui.press("tab")
      pyautogui.press("space")
    def command(obj, tag):
      try:
        Generator("tests/definition/command_test/call_notebook_toplevel.yml").get_manager()
        self.passed()
      except Exception as e:
        self.exceptions = e
    self.do_test("tests/definition/command_test/call_command.yml", command=command, test=test)
    self.assertTrue(self.success, "An error has occured.")

if __name__ == "__main__":
  unittest.main()