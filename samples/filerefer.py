import sys
from pathlib import Path
import tkinter.filedialog

sys.path.append(str(Path(__file__).parent.parent))
from tksugar import Generator

def referbutton(button, tag):
  folder = Path(__file__).parent
  filters = [("All Files", "*.*")]
  n = tkinter.filedialog.askopenfilename(filetypes = filters, initialdir = folder)
  if n != "":
    manager.vars[tag.tag["tag"]].set(n)

if __name__ == "__main__":
  gen = Generator(r"samples\yml\filerefer.yml")
  manager = gen.get_manager(commandhandler=referbutton)
  manager.mainloop()