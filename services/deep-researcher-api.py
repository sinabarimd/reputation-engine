#!/usr/bin/env python3
"""Async deep-researcher API with n8n callback."""
import json, subprocess, os, sys, http.server, threading, time, uuid
import urllib.request

PORT = 18791
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", "")
OUTPUT_DIR = "/tmp/deep-researcher-runs"
N8N_CALLBACK = "https://n8n.sinabarimd.com/webhook/research-complete"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_research_and_callback(query, site_id, content_type, selected_topic):
    """Run deep-researcher then POST results to n8n."""
    try:
        print(f"Starting research: {query[:50]}...", file=sys.stderr, flush=True)
        result = subprocess.run(
            ["deep-researcher", query,
             "--provider", "openrouter",
             "--api-key", OPENROUTER_KEY,
             "--max-iterations", "4",
             "--breadth", "3",
             "--depth", "1",
             "--output", OUTPUT_DIR],
            capture_output=True, text=True, timeout=600
        )
        
        dirs = sorted([d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))], reverse=True)
        if not dirs:
            print("No output directory", file=sys.stderr, flush=True)
            return
        
        latest = os.path.join(OUTPUT_DIR, dirs[0])
        papers = []
        report = ""
        
        papers_path = os.path.join(latest, "papers.json")
        if os.path.exists(papers_path):
            with open(papers_path) as f:
                papers = json.load(f)
        
        report_path = os.path.join(latest, "report.md")
        if os.path.exists(report_path):
            with open(report_path) as f:
                report = f.read()
        
        citable = []
        for p in papers:
            if not p.get("title"): continue
            citable.append({
                "title": p["title"],
                "url": p.get("doi_url", p.get("url", "")),
                "publication": p.get("journal", p.get("source", "")),
                "date": str(p.get("year", "")),
                "key_fact": (p.get("abstract") or "")[:200],
                "citation_count": p.get("citation_count", 0),
            })
        citable.sort(key=lambda x: (-(x.get("citation_count") or 0), -(int(str(x.get("date") or "0").split("-")[0]) if str(x.get("date","0")).replace("-","").isdigit() else 0)))
        
        print(f"Research complete: {len(papers)} papers, {len(citable)} citable", file=sys.stderr, flush=True)
        
        # Callback to n8n with results
        callback_data = json.dumps({
            "site_id": site_id,
            "selected_topic": selected_topic,
            "content_type": content_type,
            "papers_found": len(papers),
            "citable_sources": citable[:15],
            "report_excerpt": report[:2000],
        }).encode()
        
        req = urllib.request.Request(N8N_CALLBACK, data=callback_data,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=300) as resp:
            print(f"Callback response: {resp.read().decode()[:100]}", file=sys.stderr, flush=True)
            
    except Exception as e:
        print(f"Research error: {e}", file=sys.stderr, flush=True)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if "/research" not in self.path:
            self.send_error(404)
            return
        
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        query = body.get("query", "")
        site_id = body.get("site_id", "")
        content_type = body.get("content_type", "standard")
        selected_topic = body.get("selected_topic", query)
        
        if not query:
            self._json(400, {"error": "query required"})
            return
        
        # Fire and forget — run in background thread
        t = threading.Thread(target=run_research_and_callback, 
            args=(query, site_id, content_type, selected_topic))
        t.daemon = True
        t.start()
        
        # Return immediately
        self._json(200, {"status": "queued", "message": "Research started. Draft will appear in Drafts tab within 5-10 minutes."})
    
    def do_GET(self):
        self._json(200, {"status": "ok", "service": "deep-researcher-api"})
    
    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass

print(f"Deep Researcher API (async+callback) on port {PORT}", file=sys.stderr, flush=True)
http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
