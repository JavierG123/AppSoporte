import unittest

from services.system_service import compare_apps


class CompareAppsTests(unittest.TestCase):
    def test_returns_missing_when_not_installed(self) -> None:
        expected = ["Chrome", "Python", "7zip"]
        installed = ["Google Chrome", "Some App"]

        missing = compare_apps(expected, installed)

        self.assertEqual(missing, ["Python", "7zip"])

    def test_returns_empty_when_all_present(self) -> None:
        expected = ["Chrome", "Python"]
        installed = ["Google Chrome", "Python 3.11"]

        missing = compare_apps(expected, installed)

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
