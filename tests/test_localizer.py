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

  def test_haslist(self):
    """
    If you run `Localizer#_translate()` under the following conditions,
    Make sure that the items in the list are not stored.
    * YML file exists.
    * YML file contains list information.
    """
    l = Localizer("tests/definition/localizer_test/haslist.yml")
    l._prepare()
    self.assertEqual(l._translatedict["test.testc"], "")

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

  def test_localize_utf8(self):
    """
    If you run `Localizer#localize()` under the following conditions,
    Make sure that all keywords among the given data are replaced.
    * YML file exists.
    * A mixture of keywords in the dictionary and those not in the dictionary.
    * YML file contains Japanese characters.
    * The encoding of the file is UTF-8.
    """
    l = Localizer("tests/definition/localizer_test/japanese_utf8.yml")
    with open("tests/definition/localizer_test/target.yml") as f:
      data = yaml.safe_load(f)
    l.localize(data)
    self.assertEqual(data["targets"], "テストA")

  def test_localize_sjis(self):
    """
    If you run `Localizer#localize()` under the following conditions,
    Make sure that all keywords among the given data are replaced.
    * YML file exists.
    * A mixture of keywords in the dictionary and those not in the dictionary.
    * YML file contains Japanese characters.
    * The encoding of the file is Shift-JIS.
    * Specify Shift-JIS as the encoding in the Generator argument.
    """
    l = Localizer("tests/definition/localizer_test/japanese_sjis.yml", encoding="Shift_JIS")
    with open("tests/definition/localizer_test/target.yml") as f:
      data = yaml.safe_load(f)
    l.localize(data)
    self.assertEqual(data["targets"], "テストA")

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

  def test_localize_emptytext(self):
    """
    If you run `Localizer#localize()` under the following conditions,
    Ensure that no exceptions are raised and all keywords in the specified data are not replaced.
    * Specify blanks at the specified location in the YML file.
    * A mixture of keywords in the dictionary and those not in the dictionary.
    """
    l = Localizer("")
    with open("tests/definition/localizer_test/target.yml") as f:
      data = yaml.safe_load(f)
    l.localize(data)
    self.assertEqual(data["targets"], "testa")
    self.assertEqual(data["non_targets"], "no translate")
    self.assertEqual(data["listitems"], ["test.testb", "test.testc", "test.unknown"])
    self.assertEqual(data["longtext"], "test\ntest.test.testd\ntesta")

  def test_localize_nofile(self):
    """
    If you run `Localizer#localize()` under the following conditions,
    Ensure that no exceptions are raised and all keywords in the specified data are not replaced.
    * YML file not exists.
    * A mixture of keywords in the dictionary and those not in the dictionary.
    """
    l = Localizer("tests/definition/localizer_test/unknown.yml")
    with open("tests/definition/localizer_test/target.yml") as f:
      data = yaml.safe_load(f)
    l.localize(data)
    self.assertEqual(data["targets"], "testa")
    self.assertEqual(data["non_targets"], "no translate")
    self.assertEqual(data["listitems"], ["test.testb", "test.testc", "test.unknown"])
    self.assertEqual(data["longtext"], "test\ntest.test.testd\ntesta")

  #endregion

  #region Anomaly Testing

  def test_localize_sjis_noencode(self):
    """
    If you run `Localizer#localize()` under the following conditions,
    Make sure that all keywords among the given data are replaced.
    * YML file exists.
    * A mixture of keywords in the dictionary and those not in the dictionary.
    * YML file contains Japanese characters.
    * The encoding of the file is Shift-JIS.
    * The encoding of the file is Shift-JIS.
    * Do not specify the encoding in the Generator argument.
    """
    with self.assertRaises(UnicodeDecodeError):
      Localizer("tests/definition/localizer_test/japanese_sjis.yml")

  #endregion

if __name__ == "__main__":
  unittest.main()