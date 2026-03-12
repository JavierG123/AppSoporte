import tempfile
import unittest
from pathlib import Path

from config_loader import load_config


class ConfigLoaderTests(unittest.TestCase):
    def test_load_config_returns_config_when_keys_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                '{"icon":"assets/icon.png","programsFolder":"abc","genesysToolsFolder":"def"}',
                encoding="utf-8",
            )

            loaded = load_config(config_path)

            self.assertEqual(loaded["icon"], "assets/icon.png")

    def test_load_config_raises_value_error_when_missing_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text('{"icon":"assets/icon.png"}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_config(config_path)


if __name__ == "__main__":
    unittest.main()
