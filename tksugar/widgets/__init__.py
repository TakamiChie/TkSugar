"""
Widgets that require Generator-specific custom processing are stored in this package.
For example, widgets such as tkinter.ttk.Notebook that do not display child elements on the GUI just by referencing them with the master argument of child elements are recorded here.
This package is referenced with the highest priority when the Generator is executed.
Therefore, even if there is a widget with the same name in another module, this module will be called.
"""
from tksugar.widgets.generatorsupport import GeneratorSupport
from tksugar.widgets.notebook import Notebook