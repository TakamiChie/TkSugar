import sys
from pathlib import Path
import tkinter
import tkinter.filedialog


sys.path.append(str(Path(__file__).parent.parent))
from tksugar import Generator

class ReferBox(tkinter.Frame):
  """
  text box with refer button
  """
  FILEOPEN = "fileopen"
  FILESAVE = "filesave"
  ASKDIR = "askdir"

  class CommandButton(object):
    """
    An object for command button response.
    """
    def __init__(self, owner, buttonparams):
      """
      constructor
      """
      self.owner = owner
      self.buttonparams = buttonparams

    def __call__(self):
      self.owner._buttonpressed(self.buttonparams)

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

  def _buttonpressed(self, buttonparam):
    """
    Event handler that will be called when the button is clicked.

    Parameters
    ----
    buttonparam: dict[str, str]
      A list of parameters to identify the button.
    """
    o = {}
    if "filter" in buttonparam:
      o["filetypes"] = buttonparam["filter"]
    if "type" in buttonparam:
      n = ""
      if buttonparam["type"] == ReferBox.FILEOPEN:
        n = tkinter.filedialog.askopenfilename(**o)
      elif buttonparam["type"] == ReferBox.FILESAVE:
        n = tkinter.filedialog.asksaveasfilename(**o)
      elif buttonparam["type"] == ReferBox.ASKDIR:
        n = tkinter.filedialog.askdirectory(**o)
      if n != "":
        self.textbox.delete(0, tkinter.END)
        self.textbox.insert(0, n)
    if self.command:
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

  def buttons(self, buttonparams):
    """
    Define Buttons.

    Parameters
    ----
    buttonparams: list[dict[string, string]]
      Parameter list for the button.
      Since a maximum of two buttons can be defined,
      each button is defined in the list.
      caption: str
        Button's caption
      type: str
        Button's type
        fileopen: FileOpenDialog
        filesave: FileSaveDialog
        askdir: FolderChooserDialog
      filter: str
        Dialog's filter
    """
    ci = 1
    for button in buttonparams[:2]:
      b = tkinter.Button(self, text=button["caption"],
        command=self.CommandButton(self, button))
      b.grid(row=0, column=ci, ipadx=2, ipady=2)
      ci += 1
    self.grid_columnconfigure(0, weight=1)
    if self._command:
      self._command()

def change(button, tag):
  path = Path(manager.vars["multiplerefer"].get())
  manager.vars["syncrefer"].set(str(path.parent))

if __name__ == "__main__":
  gen = Generator("samples\yml\customwidget.yml", modules=["tkinter", "samples.customwidget"])
  manager = gen.get_manager(commandhandler=change)
  manager.mainloop()