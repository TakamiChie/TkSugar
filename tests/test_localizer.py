import unittest

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