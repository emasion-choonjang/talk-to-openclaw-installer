import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class InstallScriptContractTests(unittest.TestCase):
    def test_install_script_mentions_binary_asset_flow(self):
        body = (ROOT / "installer" / "install.sh").read_text(encoding="utf-8")
        self.assertIn("ASSET_URL", body)
        self.assertIn("ASSET_SHA256", body)
        self.assertIn("CURRENT_LINK", body)
        self.assertIn("launchctl bootstrap", body)


if __name__ == "__main__":
    unittest.main()
