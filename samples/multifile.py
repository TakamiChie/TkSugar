import sys
from pathlib import Path
import tkinter.filedialog

sys.path.append(str(Path(__file__).parent.parent))
from tksugar import Generator

def command(button, tag):
  pass

if __name__ == "__main__":
  gen = Generator(r"samples\yml\multifile_main.yml")
  manager = gen.get_manager(commandhandler=command)
  manager.mainloop()