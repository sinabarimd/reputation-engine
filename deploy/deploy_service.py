#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 9911

# Only allow deploys into these exact directories.
ALLOWED_DEPLOY_PATHS = [
    "/srv/sites/sinabarimd",
    "/srv/sites/sinabari-net",
    "/srv/sites/drsinabari",
    "/srv/sites/sinabariplasticsurgery",
]

# Map deploy paths to site containers that should be restarted after deploy.
SITE_CONTAINER_MAP = {
    "/srv/sites/sinabarimd": "sinabarimd-static",
    "/srv/sites/sinabari-net": "sinabari-net-static",
    "/srv/sites/drsinabari": "drsinabari-static",
    "/srv/sites/sinabariplasticsurgery": "sinabariplasticsurgery-static",
}

# Optional shared secret for the deploy endpoint.
DEPLOY_TOKEN = os.environ.get("DEPLOY_TOKEN", "")

# Profile pack support
PROFILE_DIR = Path("/opt/openclaw-deployer/site_profiles")
ALLOWED_PROFILE_FILES = {
    "sinabarimd_com.yaml",
    "sinabari_net.yaml",
    "drsinabari_com.yaml",
    "sinabariplasticsurgery_com.yaml",
    "network_rules.yaml",
    "web2_support_profiles.yaml",
    "README.txt",
}


def json_response(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def safe_relpath(p: str) -> bool:
    if not p or p.startswith("/") or p.startswith("\\"):
        return False
    parts = Path(p).parts
    if any(part in ("..", "") for part in parts):
        return False
    return True


def normalize_permissions(path: Path):
    subprocess.run(["chmod", "755", str(path)], check=True)
    subprocess.run(
        f"find {path} -type d -exec chmod 755 {{}} \\;",
        shell=True,
        check=True,
    )
    subprocess.run(
        f"find {path} -type f -exec chmod 644 {{}} \\;",
        shell=True,
        check=True,
    )


def restart_site_container(deploy_path: str):
    container = SITE_CONTAINER_MAP.get(deploy_path)
    if not container:
        return
    subprocess.run(["docker", "restart", container], check=True)


class DeployHandler(BaseHTTPRequestHandler):
    server_version = "OpenClawDeployer/0.2"

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {fmt % args}")

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            return json_response(self, 200, {"ok": True, "service": "openclaw-deployer"})

        if parsed.path.startswith("/profiles/"):
            filename = parsed.path.split("/profiles/", 1)[1]

            if filename not in ALLOWED_PROFILE_FILES:
                return json_response(self, 404, {"ok": False, "error": "Profile not found"})

            file_path = PROFILE_DIR / filename
            if not file_path.exists():
                return json_response(self, 404, {"ok": False, "error": "Profile file missing"})

            body = file_path.read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        return json_response(self, 404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        if self.path != "/deploy":
            return json_response(self, 404, {"ok": False, "error": "Not found"})

        if DEPLOY_TOKEN:
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {DEPLOY_TOKEN}":
                return json_response(self, 401, {"ok": False, "error": "Unauthorized"})

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
        except Exception as e:
            return json_response(self, 400, {"ok": False, "error": f"Invalid JSON: {e}"})

        deploy_path = payload.get("deployPath")
        files = payload.get("files")

        if deploy_path not in ALLOWED_DEPLOY_PATHS:
            return json_response(self, 400, {"ok": False, "error": "deployPath not allowed"})

        if not isinstance(files, list) or not files:
            return json_response(self, 400, {"ok": False, "error": "files must be a non-empty list"})

        target = Path(deploy_path)
        parent = target.parent
        parent.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        temp_dir = Path(tempfile.mkdtemp(prefix=f"{target.name}.tmp.", dir=str(parent)))
        backup_dir = parent / f"{target.name}.backup.{ts}"

        try:
            for entry in files:
                rel = entry.get("path")
                content = entry.get("content")

                if not isinstance(rel, str) or not safe_relpath(rel):
                    raise ValueError(f"Invalid file path: {rel}")

                if not isinstance(content, str):
                    raise ValueError(f"Invalid content for: {rel}")

                out_path = temp_dir / rel
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(content, encoding="utf-8")

            normalize_permissions(temp_dir)

            if target.exists():
                if backup_dir.exists():
                    raise RuntimeError(f"Backup path already exists: {backup_dir}")
                target.rename(backup_dir)

            temp_dir.rename(target)
            normalize_permissions(target)
            restart_site_container(deploy_path)

            self.send_response(204)
            self.end_headers()
            return

        except Exception as e:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
            return json_response(self, 500, {"ok": False, "error": str(e)})


if __name__ == "__main__":
    print(f"Starting deploy service on {HOST}:{PORT}")
    HTTPServer((HOST, PORT), DeployHandler).serve_forever()
