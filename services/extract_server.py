#!/usr/bin/env python3
"""
Text Extraction Service — extracts plain text from PDF, DOCX, TXT, MD files.
Listens on port 9913. POST /extract with JSON: {data: base64, filename: str, topic_id: str}
Returns: {text, chars, source_filename, saved_path}
"""
import base64
import json
import os
import re
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 9913
ATTACHMENTS_DIR = '/srv/sites/research-attachments'
MAX_TEXT_CHARS = 50000


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body):
        data = json.dumps(body).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == '/health':
            return self._send(200, {'ok': True, 'service': 'text-extract'})
        return self._send(404, {'ok': False})

    def do_POST(self):
        if self.path != '/extract':
            return self._send(404, {'ok': False, 'error': 'not found'})
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length).decode('utf-8') if length else '{}'
            body = json.loads(raw)

            b64_data = body.get('data')
            filename = body.get('filename', '')
            topic_id = body.get('topic_id', 'unnamed')

            if not b64_data or not filename:
                return self._send(400, {'ok': False, 'error': 'data and filename required'})

            file_bytes = base64.b64decode(b64_data)
            if len(file_bytes) > 2.5 * 1024 * 1024:
                return self._send(400, {'ok': False, 'error': 'file too large (max ~2MB)'})

            ext = os.path.splitext(filename)[1].lower()
            text = self._extract(ext, file_bytes)

            if text is None:
                return self._send(400, {'ok': False, 'error': f'unsupported file type: {ext}'})

            text = text[:MAX_TEXT_CHARS]

            # Save to filesystem
            safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', topic_id)[:120]
            os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
            save_path = os.path.join(ATTACHMENTS_DIR, f'{safe_id}.txt')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)

            return self._send(200, {
                'ok': True,
                'text': text,
                'chars': len(text),
                'source_filename': filename,
                'saved_path': save_path,
            })

        except base64.binascii.Error:
            return self._send(400, {'ok': False, 'error': 'invalid base64 data'})
        except Exception as e:
            return self._send(500, {'ok': False, 'error': str(e)})

    def _extract(self, ext, file_bytes):
        if ext in ('.txt', '.md'):
            return file_bytes.decode('utf-8', errors='replace')

        elif ext == '.pdf':
            from pdfminer.high_level import extract_text
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            try:
                return extract_text(tmp_path)
            finally:
                os.unlink(tmp_path)

        elif ext == '.docx':
            from docx import Document
            import io
            doc = Document(io.BytesIO(file_bytes))
            return '\n'.join(p.text for p in doc.paragraphs)

        return None


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'text-extract service listening on :{PORT}', flush=True)
    server.serve_forever()
