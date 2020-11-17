import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from tksugar import Generator

def menuitem(button, tag):
  pass

def changevar(obj, name):
  print(f"{name} changed! {obj.get()}")

if __name__ == "__main__":
  gen = Generator("samples\yml\menu.yml")
  manager = gen.get_manager(commandhandler=menuitem)
  manager.trace_handler = changevar;
  manager.mainloop()