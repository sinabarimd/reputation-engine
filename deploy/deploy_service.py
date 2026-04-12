#!/usr/bin/env python3
"""
Reputation Engine — Deterministic File-Sync Deploy Service

A lightweight HTTP server that receives a file manifest and atomically
syncs a site directory. Files not in the manifest are removed, ensuring
the deployed state always matches exactly what the pipeline specifies.

Designed to run as a systemd service on the host, accessible from
Docker containers via host.docker.internal.

Usage:
    python deploy_service.py --port 9911 --base-dir /srv/sites

Environment:
    DEPLOY_SERVICE_KEY  — Bearer token for authentication
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("deploy-service")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEPLOY_KEY = os.environ.get("DEPLOY_SERVICE_KEY", "")
BASE_DIR = "/srv/sites"
MAX_PAYLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

# Domain → deploy directory mapping
DOMAIN_MAP = {
    "sinabarimd.com": "sinabarimd",
    "sinabari.net": "sinabari-net",
    "drsinabari.com": "drsinabari",
    "sinabariplasticsurgery.com": "sinabariplasticsurgery",
}


# ---------------------------------------------------------------------------
# Deploy Logic
# ---------------------------------------------------------------------------

def validate_payload(payload: dict) -> tuple[bool, str]:
    """Validate the deploy payload structure."""
    required = ["domain", "deployPath", "files"]
    for key in required:
        if key not in payload:
            return False, f"Missing required field: {key}"

    if not isinstance(payload["files"], list):
        return False, "files must be an array"

    if len(payload["files"]) == 0:
        return False, "files array is empty — refusing to deploy (would wipe site)"

    for i, f in enumerate(payload["files"]):
        if "path" not in f or "content" not in f:
            return False, f"File entry {i} missing 'path' or 'content'"
        # Prevent path traversal
        normalized = os.path.normpath(f["path"])
        if normalized.startswith("..") or normalized.startswith("/"):
            return False, f"Invalid file path: {f['path']}"

    return True, "ok"


def compute_manifest_hash(files: list[dict]) -> str:
    """Compute a deterministic hash of the file manifest for release tracking."""
    hasher = hashlib.sha256()
    for f in sorted(files, key=lambda x: x["path"]):
        hasher.update(f["path"].encode())
        hasher.update(f["content"].encode())
    return hasher.hexdigest()[:12]


def execute_deploy(deploy_path: str, files: list[dict], release_id: str = None) -> dict:
    """
    Execute a full-file-sync deploy.

    1. Write all files from the manifest
    2. Remove any files NOT in the manifest
    3. Return a summary of what changed
    """
    deploy_dir = Path(deploy_path)
    deploy_dir.mkdir(parents=True, exist_ok=True)

    manifest_paths = set()
    files_written = 0
    files_unchanged = 0
    files_removed = 0

    # Phase 1: Write all files from manifest
    for file_entry in files:
        rel_path = file_entry["path"]
        content = file_entry["content"]
        full_path = deploy_dir / rel_path
        manifest_paths.add(rel_path)

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file already exists with same content
        if full_path.exists():
            existing = full_path.read_text(encoding="utf-8", errors="replace")
            if existing == content:
                files_unchanged += 1
                continue

        # Write the file
        full_path.write_text(content, encoding="utf-8")
        files_written += 1
        log.info(f"  wrote: {rel_path}")

    # Phase 2: Remove files not in manifest (full sync)
    for root, dirs, filenames in os.walk(deploy_dir):
        for filename in filenames:
            full_path = Path(root) / filename
            rel_path = str(full_path.relative_to(deploy_dir))
            if rel_path not in manifest_paths:
                full_path.unlink()
                files_removed += 1
                log.info(f"  removed: {rel_path}")

    # Phase 3: Clean up empty directories
    for root, dirs, filenames in os.walk(deploy_dir, topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            if not any(dir_path.iterdir()):
                dir_path.rmdir()

    manifest_hash = compute_manifest_hash(files)

    result = {
        "success": True,
        "deploy_path": str(deploy_dir),
        "release_id": release_id or manifest_hash,
        "manifest_hash": manifest_hash,
        "files_written": files_written,
        "files_unchanged": files_unchanged,
        "files_removed": files_removed,
        "total_files": len(files),
        "deployed_at": datetime.now(timezone.utc).isoformat(),
    }

    log.info(
        f"Deploy complete: {files_written} written, "
        f"{files_unchanged} unchanged, {files_removed} removed"
    )

    return result


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class DeployHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log.info(f"{self.client_address[0]} - {format % args}")

    def send_json(self, status: int, data: dict):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def check_auth(self) -> bool:
        if not DEPLOY_KEY:
            return True  # No key configured = no auth required
        auth = self.headers.get("Authorization", "")
        if auth == f"Bearer {DEPLOY_KEY}":
            return True
        self.send_json(401, {"error": "Unauthorized"})
        return False

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "service": "deploy-service"})
        elif self.path.startswith("/profiles/"):
            self.handle_profile_request()
        else:
            self.send_json(404, {"error": "Not found"})

    def handle_profile_request(self):
        """Serve site profile YAML files."""
        profile_name = self.path.split("/profiles/")[-1]
        profile_path = Path(BASE_DIR) / "profiles" / profile_name
        if profile_path.exists() and profile_path.suffix in (".yaml", ".yml"):
            content = profile_path.read_text()
            self.send_response(200)
            self.send_header("Content-Type", "text/yaml")
            self.end_headers()
            self.wfile.write(content.encode())
        else:
            self.send_json(404, {"error": f"Profile not found: {profile_name}"})

    def do_POST(self):
        if self.path != "/deploy":
            self.send_json(404, {"error": "Not found"})
            return

        if not self.check_auth():
            return

        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > MAX_PAYLOAD_BYTES:
            self.send_json(413, {"error": "Payload too large"})
            return

        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            self.send_json(400, {"error": f"Invalid JSON: {e}"})
            return

        # Validate
        valid, msg = validate_payload(payload)
        if not valid:
            self.send_json(400, {"error": msg})
            return

        domain = payload["domain"]
        deploy_path = payload["deployPath"]
        files = payload["files"]
        release_id = payload.get("release_id")
        verify_url = payload.get("verifyUrl")

        log.info(f"Deploy request: {domain} → {deploy_path} ({len(files)} files)")

        # Verify deploy path is under BASE_DIR
        resolved = os.path.realpath(deploy_path)
        if not resolved.startswith(os.path.realpath(BASE_DIR)):
            self.send_json(400, {"error": "Deploy path outside base directory"})
            return

        # Execute deploy
        try:
            result = execute_deploy(deploy_path, files, release_id)
            if verify_url:
                result["verify_url"] = verify_url
            self.send_json(200, result)
        except Exception as e:
            log.error(f"Deploy failed: {e}", exc_info=True)
            self.send_json(500, {"error": f"Deploy failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Reputation Engine Deploy Service")
    parser.add_argument("--port", type=int, default=9911, help="Port to listen on")
    parser.add_argument("--base-dir", default=BASE_DIR, help="Base directory for sites")
    args = parser.parse_args()

    global BASE_DIR
    BASE_DIR = args.base_dir

    if not DEPLOY_KEY:
        log.warning("DEPLOY_SERVICE_KEY not set — running without authentication")

    server = HTTPServer(("0.0.0.0", args.port), DeployHandler)
    log.info(f"Deploy service listening on port {args.port}")
    log.info(f"Base directory: {BASE_DIR}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down")
        server.server_close()


if __name__ == "__main__":
    main()
