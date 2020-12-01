import locale

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
    with open(file, "r") as f:
      self.string = f.read()
    self._translatedict = None

  def _prepare(self):
    """
    Read and prepare the data list.
    """
    def flatten_dict(basename, struct):
      result = {}
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

  def translate(self, data):
    """
    Translate the given data.
    This method modifies the given data directly.

    Parameters
    ----
    data: dict
      Data list.
    """
    def translate_core(data):
      for k in data.keys():
        if type(data[k]) is dict:
          translate_core(data[k])
        elif type(data[k]) is str and data[k].startswith(":::"):
          data[k] = self._translate(data[k][3:])
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
    """
    return self._translatedict[name]