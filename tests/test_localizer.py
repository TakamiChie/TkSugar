import unittest

import yaml

from tksugar.localizer import Localizer

class Test_Localizer(unittest.TestCase):
  """
  Tests the `Localizer` Class
  """

  #region Testing for normal operation

  def test_prepare(self):
    """
    Confirm that the translation data can be read correctly when `Localizer#_prepare()` is executed under the following conditions.
    * YML file exists.
    * YML file has a tree structure
    """
    l = Localizer("tests/definition/localizer_test/safecase.yml")
    l._prepare()
    self.assertEqual(len(l._translatedict), 4)
    self.assertEqual(l._translatedict["testa"], "a")
    self.assertEqual(l._translatedict["test.testb"], "b")
    self.assertEqual(l._translatedict["test.testc"], "c")
    self.assertEqual(l._translatedict["test.test.testd"], "d")

  def test_translate(self):
    """
    If you run `Localizer#_translate()` under the following conditions,
    make sure that the string specified as an argument will be replaced by a string in the dictionary.
    * After executing `Localizer#_prepare()`.
    * The keywords present in the dictionary.
    """
    l = Localizer("tests/definition/localizer_test/safecase.yml")
    l._prepare()
    self.assertEqual(l._translate("testa"), "a")
    self.assertEqual(l._translate("test.testb"), "b")

  def test_localize(self):
    """
    If you run `Localizer#localize()` under the following conditions,
    Make sure that all keywords among the given data are replaced.
    * YML file exists.
    * A mixture of keywords in the dictionary and those not in the dictionary.
    """
    l = Localizer("tests/definition/localizer_test/safecase.yml")
    with open("tests/definition/localizer_test/target.yml") as f:
      data = yaml.safe_load(f)
    l.localize(data)
    self.assertEqual(data["targets"], "a")
    self.assertEqual(data["non_targets"], "no translate")
    self.assertEqual(data["listitems"], ["b", "c", "test.unknown"])
    self.assertEqual(data["longtext"], "test\nd\na")

  #endregion

  #region Semi-normal behavior testing

  def test_translate_nodict(self):
    """
    If you run `Localizer#_translate()` under the following conditions,
    make sure that the string specified as an argument not be replaced.
    * After executing `Localizer#_prepare()`.
    * The keywords not present in the dictionary.
    """
    l = Localizer("tests/definition/localizer_test/safecase.yml")
    l._prepare()
    self.assertEqual(l._translate("testb"), "testb")
    self.assertEqual(l._translate("test.testd"), "test.testd")

  #endregion

  #region Anomaly Testing

  def test_haslist(self):
    """
    Make sure ValueError is raised when `Localizer#_prepare()` is executed under the following conditions.
    * YML file exists.
    * YML file contains list information.
    """
    l = Localizer("tests/definition/localizer_test/haslist.yml")
    with self.assertRaises(ValueError) as cm:
      l._prepare()
      self.assertEqual(str(cm.exception), "The list can not be included.")

  #endregion

if __name__ == "__main__":
  unittest.main()