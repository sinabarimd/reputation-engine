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

# Fallback: expose the current output.yaml from each publisher agent's workspace so
# the Content Generator can recover an article when the OpenClaw gateway returns its
# "No response from OpenClaw." fallback string despite the agent having written the
# file. Freshness cap prevents serving a stale file from a previous generation.
OPENCLAW_WORKSPACE_ROOT = Path("/root/.openclaw-default")
SITE_TO_WORKSPACE_SLUG = {
    "sinabarimd": "sinabarimd",
    "sinabari_net": "sinabari-net",
    "drsinabari": "drsinabari",
    "sinabariplasticsurgery": "sinabariplasticsurgery",
}
WORKSPACE_OUTPUT_MAX_AGE_SEC = 600  # 10 minutes


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

        if parsed.path.startswith("/workspace-output/"):
            if DEPLOY_TOKEN:
                auth = self.headers.get("Authorization", "")
                if auth != f"Bearer {DEPLOY_TOKEN}":
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
            site_id = parsed.path.split("/workspace-output/", 1)[1].strip("/")
            slug = SITE_TO_WORKSPACE_SLUG.get(site_id)
            if not slug:
                return json_response(self, 404, {"ok": False, "error": "Unknown site_id"})
            yaml_path = OPENCLAW_WORKSPACE_ROOT / f"workspace-publisher-{slug}" / "output.yaml"
            if not yaml_path.exists():
                return json_response(self, 404, {"ok": False, "error": "No output.yaml in workspace"})
            try:
                mtime = yaml_path.stat().st_mtime
            except OSError as e:
                return json_response(self, 500, {"ok": False, "error": str(e)})
            age = datetime.now(timezone.utc).timestamp() - mtime
            if age > WORKSPACE_OUTPUT_MAX_AGE_SEC:
                return json_response(self, 410, {
                    "ok": False,
                    "error": "Workspace output.yaml is stale",
                    "age_sec": int(age),
                    "max_age_sec": WORKSPACE_OUTPUT_MAX_AGE_SEC,
                })
            try:
                body = yaml_path.read_text(encoding="utf-8")
            except OSError as e:
                return json_response(self, 500, {"ok": False, "error": str(e)})
            return json_response(self, 200, {
                "ok": True,
                "site_id": site_id,
                "yaml_path": str(yaml_path),
                "age_sec": int(age),
                "bytes": len(body),
                "content": body,
            })

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
        # /fetch-image: download a public URL to an assets path (used by Content Generator to attach article images)
        if self.path == "/fetch-image":
            if DEPLOY_TOKEN:
                auth = self.headers.get("Authorization", "")
                if auth != f"Bearer {DEPLOY_TOKEN}":
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                payload = json.loads(raw.decode("utf-8"))
                src_url = payload.get("src_url")
                dest_path = payload.get("dest_path", "")
                if not src_url or not dest_path:
                    return json_response(self, 400, {"ok": False, "error": "src_url and dest_path required"})
                ALLOWED_PREFIXES = (
                    "sinabariplasticsurgery/article-images/",
                    "sinabari-net/article-images/",
                    "drsinabari/article-images/",
                    "sinabarimd/article-images/",
                )
                if not any(dest_path.startswith(p) for p in ALLOWED_PREFIXES):
                    return json_response(self, 400, {"ok": False, "error": f"dest_path must start with {ALLOWED_PREFIXES}"})
                if ".." in dest_path or dest_path.startswith("/"):
                    return json_response(self, 400, {"ok": False, "error": "invalid dest_path"})
                import urllib.request
                req = urllib.request.Request(src_url, headers={"User-Agent": "OpenClawDeployer/0.3 (article-image-fetcher)"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    content_type = resp.headers.get("Content-Type", "")
                    if not content_type.startswith("image/"):
                        return json_response(self, 400, {"ok": False, "error": f"Not an image ({content_type})"})
                    data = resp.read()
                out = Path("/srv/assets") / dest_path
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
                os.chmod(str(out), 0o644)
                return json_response(self, 200, {"ok": True, "saved_bytes": len(data), "dest": str(out), "content_type": content_type})
            except Exception as e:
                return json_response(self, 500, {"ok": False, "error": str(e)})

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

                content_b64 = entry.get('content_b64')

                if content is None and content_b64 is None:
                    raise ValueError(f"Missing content for: {rel}")
                if content is not None and not isinstance(content, str):
                    raise ValueError(f"Invalid content for: {rel}")
                if content_b64 is not None and not isinstance(content_b64, str):
                    raise ValueError(f"Invalid content_b64 for: {rel}")

                out_path = temp_dir / rel
                out_path.parent.mkdir(parents=True, exist_ok=True)
                if content_b64 is not None:
                    import base64
                    out_path.write_bytes(base64.b64decode(content_b64))
                else:
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
