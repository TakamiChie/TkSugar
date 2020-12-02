from pathlib import Path
import re

from yaml.loader import SafeLoader

class Localizer(object):
  """
  Translates all text of the specified data based on the dictionary data for translation.
  The string to be translated in the data list is decorated with three colons (:::) (ex. `:::text`)

  The operation of this class is to replace the character string to be translated with the text in the dictionary data.

  Dictionary data can have a hierarchical structure.
  Data with a hierarchical structure is expanded into a character string delimited during translation processing.
  """
  def __init__(self, file):
    """
    Constructor.

    Parameters
    ----
    file: str
      The path to the YAML file that contains the translation string.
    """
    self.string = ""
    p = Path(file)
    if p.exists():
      with open(p, "r") as f:
        self.string = f.read()
    self._translatedict = None

  def _prepare(self):
    """
    Read and prepare the data list.
    """
    def flatten_dict(basename, struct):
      result = {}
      if type(struct) is dict:
        for k in struct.keys():
          if type(struct[k]) is dict:
            result.update(flatten_dict(f"{basename}{k}.", struct[k]))
          elif type(struct[k]) is list:
            raise ValueError("The list can not be included.")
          else:
            result[f"{basename}{k}"] = struct[k]
      return result
    if self._translatedict is None:
      # Read
      loader = SafeLoader(self.string)
      try:
        data = loader.get_single_data()
      finally:
        loader.dispose()
      self._translatedict = flatten_dict("", data)

  def localize(self, data):
    """
    Translate the given data.
    This method modifies the given data directly.

    Parameters
    ----
    data: dict
      Data list.
    """
    def translate_core(data):
      for k in data.keys() if type(data) is dict else range(len(data)):
        if type(data[k]) is dict:
          translate_core(data[k])
        elif type(data[k]) is list:
          translate_core(data[k])
        elif type(data[k]) is str:
          data[k] = rexp.sub(lambda m: self._translate(m.group(0)[3:]), data[k])
    rexp = re.compile(r":::\S+")
    self._prepare()
    translate_core(data)

  def _translate(self, name):
    """
    Perform translation processing.

    Parameters
    ----
    name: str
      Keyword name.

    Returns
    ----
    return: str
      The string after replacement.
      If the keywords were not present in the dictionary, the string is returned as is without replacement.
    """
    return self._translatedict[name] if name in self._translatedict else name
