import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class StableManifestContractTests(unittest.TestCase):
    def test_stable_manifest_contains_required_fields(self):
        payload = json.loads((ROOT / "stable.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["channel"], "stable")
        self.assertTrue(payload["version"])
        self.assertIn("asset_url", payload)
        self.assertIn("sha256", payload)
        self.assertIn("install_script_url", payload)
        self.assertIn("blocked_versions", payload)

    def test_pyinstaller_spec_exists(self):
        self.assertTrue((ROOT / "installer" / "pyinstaller" / "bridge.spec").exists())


if __name__ == "__main__":
    unittest.main()
