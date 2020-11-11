import sys
from pathlib import Path
import tkinter

sys.path.append(str(Path(__file__).parent.parent))
from tksugar import Generator

if __name__ == "__main__":
  gen = Generator(r"samples\yml\notebook.yml")
  man = gen.get_manager()
  # list set
  w = man.widgets["list"].widget
  [w.insert(tkinter.END, f"item {n}") for n in range(1,5)]
  w.select_set(1)
  # canvas set
  w = man.widgets["canvas"].widget
  w.create_oval(10, 5, 90, 30, fill="red")
  w.create_oval(10, 20, 90, 45, fill="blue")
  w.create_text(50, 25, text="canvas", fill="green")
  man.mainloop()