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

    def test_install_script_prunes_old_bridge_releases(self):
        body = (ROOT / "installer" / "install.sh").read_text(encoding="utf-8")
        self.assertIn("prune_old_releases", body)
        self.assertIn("RELEASES_DIR", body)
        self.assertIn("remove_legacy_runtime", body)
        self.assertIn(".local/share/sori-bridge", body)

    def test_install_script_exports_openclaw_runtime_path(self):
        body = (ROOT / "installer" / "install.sh").read_text(encoding="utf-8")
        self.assertIn("detect_openclaw_bin", body)
        self.assertIn("detect_node_bin", body)
        self.assertIn("OPENCLAW_BIN</key>", body)
        self.assertIn("PATH</key>", body)


if __name__ == "__main__":
    unittest.main()
