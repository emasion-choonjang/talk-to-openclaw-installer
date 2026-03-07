import importlib.util
import pathlib
import tempfile
import unittest
from unittest import mock

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "installer" / "sori_agent.py"
spec = importlib.util.spec_from_file_location("sori_agent", MODULE_PATH)
sori_agent = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(sori_agent)


class EnsureBridgeScriptTests(unittest.TestCase):
    def test_downloads_bridge_script_to_install_home(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b"print('ok')\n"

        with tempfile.TemporaryDirectory() as td:
            install_home = pathlib.Path(td)
            with mock.patch.object(sori_agent.urllib.request, "urlopen", return_value=Response()):
                ok, payload = sori_agent.ensure_bridge_script("https://example.com/bridge.py", install_home)
            self.assertTrue(ok)
            bridge_path = pathlib.Path(payload)
            self.assertTrue(bridge_path.exists())
            self.assertEqual(bridge_path.read_text(encoding="utf-8"), "print('ok')\n")

    def test_returns_error_on_download_failure(self):
        with tempfile.TemporaryDirectory() as td:
            install_home = pathlib.Path(td)
            with mock.patch.object(sori_agent.urllib.request, "urlopen", side_effect=RuntimeError("boom")):
                ok, payload = sori_agent.ensure_bridge_script("https://example.com/bridge.py", install_home)
            self.assertFalse(ok)
            self.assertIn("bridge_script_download_failed", payload)


class WritePlistTests(unittest.TestCase):
    def test_writes_expected_environment(self):
        with tempfile.TemporaryDirectory() as td:
            home = pathlib.Path(td)
            launch_agents = home / "Library" / "LaunchAgents"
            with mock.patch.object(pathlib.Path, "home", return_value=home), mock.patch.object(
                sori_agent, "detect_openclaw_bin", return_value="/opt/homebrew/bin/openclaw"
            ):
                plist = sori_agent.write_plist(
                    py_bin="/tmp/venv/bin/python",
                    bridge_script="/tmp/sori/run_mock_openclaw_server.py",
                    work_dir="/tmp/sori",
                    port=18890,
                    public_host="192.168.0.10",
                    tts_engine="edge",
                    openclaw_agent="sori-bridge",
                    openclaw_thinking="minimal",
                    installer_bootstrap_url="https://example.com/sori_agent.py",
                )
            self.assertEqual(plist, launch_agents / "ai.sori.bridge.plist")
            body = plist.read_text(encoding="utf-8")
            self.assertIn("OPENCLAW_DEFAULT_AGENT</key><string>sori-bridge", body)
            self.assertIn("INSTALLER_BOOTSTRAP_URL</key><string>https://example.com/sori_agent.py", body)
            self.assertIn("OPENCLAW_BIN</key><string>/opt/homebrew/bin/openclaw", body)
            self.assertIn("OPENCLAW_PUBLIC_HOST</key><string>192.168.0.10", body)


class CmdInstallTests(unittest.TestCase):
    def test_install_uses_downloaded_bridge_script(self):
        args = mock.Mock(
            install_home="/tmp/install-home",
            bridge_script_url="https://example.com/bridge.py",
            python="python3",
            venv_dir="/tmp/venv",
            skip_deps=True,
            requirements="/tmp/requirements.txt",
            bridge_port=18890,
            public_host="192.168.0.10",
            tts_engine="edge",
            openclaw_agent="sori-bridge",
            openclaw_model="anthropic/claude-haiku-4-5",
            openclaw_workspace="/tmp/workspace",
            openclaw_thinking="minimal",
            installer_bootstrap_url="https://example.com/sori_agent.py",
            pairing_code="ABC123",
        )
        with mock.patch.object(sori_agent, "ensure_bridge_script", return_value=(True, "/tmp/install-home/run_mock_openclaw_server.py")), mock.patch.object(
            sori_agent, "ensure_venv_python", return_value=(True, "/tmp/venv/bin/python")
        ), mock.patch.object(
            sori_agent, "write_plist", return_value=pathlib.Path("/tmp/ai.sori.bridge.plist")
        ) as write_plist, mock.patch.object(
            sori_agent, "ensure_openclaw_agent_config", return_value=(True, {"agent": "sori-bridge"})
        ), mock.patch.object(
            sori_agent, "bootstrap", return_value={"ok": True}
        ), mock.patch.object(
            sori_agent, "start_service", return_value={"ok": True}
        ), mock.patch.object(
            pathlib.Path, "mkdir"
        ), mock.patch(
            "builtins.print"
        ):
            rc = sori_agent.cmd_install(args)
        self.assertEqual(rc, 0)
        write_plist.assert_called_once()
        self.assertEqual(write_plist.call_args.args[1], "/tmp/install-home/run_mock_openclaw_server.py")


if __name__ == "__main__":
    unittest.main()
