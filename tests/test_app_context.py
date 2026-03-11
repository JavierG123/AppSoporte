import unittest
from pathlib import Path

from app_context import AppContext


class AppContextTests(unittest.TestCase):
    def test_builds_expected_paths(self) -> None:
        ctx = AppContext(root_path=Path("C:/Soporte"))

        self.assertEqual(ctx.installers_path, Path("C:/Soporte/Instaladores"))
        self.assertEqual(ctx.tools_path, Path("C:/Soporte/Herramientas"))

    def test_allows_custom_directory_names(self) -> None:
        ctx = AppContext(
            root_path=Path("C:/Soporte"),
            installers_dir_name="Setup",
            tools_dir_name="Tools",
        )

        self.assertEqual(ctx.installers_path, Path("C:/Soporte/Setup"))
        self.assertEqual(ctx.tools_path, Path("C:/Soporte/Tools"))


if __name__ == "__main__":
    unittest.main()
