import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from tksugar import Generator

if __name__ == "__main__":
  gen = Generator("samples\yml\calc.yml")
  manager = gen.get_manager()
  manager.mainloop()