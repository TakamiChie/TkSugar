import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from tksugar import Generator

count = 1

def button(button, tag):
  global count
  child = Generator(r"samples\yml\multiwindow_child.yml").get_manager()
  ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]) # https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
  child.widgets["label"].widget["text"] = f"This is {ordinal(count)} Child Window"
  if owner.vars["modal"].get():
    child.window.grab_set()
  count += 1

if __name__ == "__main__":
  gen = Generator(r"samples\yml\multiwindow_owner.yml")
  owner = gen.get_manager(commandhandler=button)
  owner.mainloop()