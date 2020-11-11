import tkinter.ttk


from tksugar.widgets.generatorsupport import GeneratorSupport

class Notebook(tkinter.ttk.Notebook, GeneratorSupport):
  """
  `tkinter.ttk.Notebook` with added methods to support Generator.
  """
  def append_child(self, child, **params):
    self.add(child, **params)