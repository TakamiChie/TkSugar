import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from tksugar import Generator

def calcbutton(button, tag):
  text = button["text"]
  var = manager.vars["label"]
  calctext = var.get()
  result = ""
  if text == "C":
    # Clear.
    if len(calctext) > 0:
      result = calctext[:-1]
  elif text == "AC":
    # All clear.
    result = ""
  elif text == "=":
    # Set the calculation result.
    try:
      result = eval(calctext)
    except SyntaxError:
      pass
  elif text == "%":
    # Multiply the calculation result by 0.01
    if len(calctext) == 0:
      return
    if calctext[-1] in [".", "+", "-", "*", "/"]:
      calctext = calctext[:-1]
    var.set(calctext + "*0.01")
    manager.widgets["equal"].performclick()
    return
  else:
    # Do not press the button if the operator or calculation string is empty immediately before.
    if text in ["+", "-", "*", "/"]:
      if calctext == "" or calctext[-1] in ["+", "-", "*", "/"]:
        return
    # Do not allow multiple periods to be entered.
    if text == "." and "." in calctext:
      return
    result = calctext + str(text)
  var.set(result)

if __name__ == "__main__":
  gen = Generator("samples\yml\calc.yml")
  manager = gen.get_manager(commandhandler=calcbutton)
  manager.mainloop()