import sys
from pathlib import Path

from tksugar import Generator

if __name__ == "__main__":
  gen = Generator(r"samples\yml\localize_target.yml", localization_file="samples\yml\localize_script.yml")
  man = gen.get_manager()
  man.mainloop()