import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class StableManifestContractTests(unittest.TestCase):
    def test_stable_manifest_contains_required_fields(self):
        path = ROOT / "stable.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["channel"], "stable")
        self.assertTrue(payload["version"])
        self.assertIn("asset_url", payload)
        self.assertIn("sha256", payload)
        self.assertIn("install_script_url", payload)
        self.assertIn("blocked_versions", payload)

    def test_pyinstaller_spec_exists(self):
        spec = ROOT / "installer" / "pyinstaller" / "bridge.spec"
        self.assertTrue(spec.exists())

    def test_pyinstaller_spec_packages_macos_runtime_bits(self):
        spec = (ROOT / "installer" / "pyinstaller" / "bridge.spec").read_text(encoding="utf-8")
        self.assertIn('collect_data_files("faster_whisper")', spec)
        self.assertIn('collect_dynamic_libs("ctranslate2")', spec)
        self.assertIn('"_scproxy"', spec)

    def test_bridge_runtime_enforces_single_instance_before_warmup(self):
        body = (ROOT / "installer" / "run_mock_openclaw_server.py").read_text(encoding="utf-8")
        self.assertNotIn("import multiprocessing", body)
        self.assertIn("def acquire_instance_lock", body)
        self.assertIn("bridge_already_running_on_port_", body)
        self.assertIn("ThreadingHTTPServer((HOST, PORT), Handler)", body)
        self.assertIn('threading.Thread(target=warmup_stt_runtime, daemon=True, name="stt-warmup").start()', body)
        self.assertLess(
            body.index("ThreadingHTTPServer((HOST, PORT), Handler)"),
            body.index('threading.Thread(target=warmup_stt_runtime, daemon=True, name="stt-warmup").start()'),
        )


if __name__ == "__main__":
    unittest.main()
