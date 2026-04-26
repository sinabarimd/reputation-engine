#!/usr/bin/env python3
"""GSC Measurement Script — run locally or via cron.
Queries Google Search Console for all 3 sites and pushes results to the Measurement Agent.
Usage: python3 measure.py
"""
import json, time, base64, ssl, sys, os
from urllib.request import Request, urlopen, build_opener, HTTPSHandler, install_opener
from urllib.parse import urlencode
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_PATH = os.path.join(SCRIPT_DIR, 'gsc-service-account.json')
N8N_WEBHOOK = 'https://YOUR_N8N_DOMAIN/webhook'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
install_opener(build_opener(HTTPSHandler(context=ctx)))

def get_access_token():
    with open(SA_PATH) as f:
        sa = json.load(f)
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode()).rstrip(b'=')
    now = int(time.time())
    claims = {"iss": sa["client_email"], "scope": "https://www.googleapis.com/auth/webmasters.readonly",
              "aud": sa["token_uri"], "iat": now, "exp": now + 3600}
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b'=')
    pk = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = pk.sign(header + b'.' + payload, padding.PKCS1v15(), hashes.SHA256())
    jwt = (header + b'.' + payload + b'.' + base64.urlsafe_b64encode(sig).rstrip(b'=')).decode()
    resp = urlopen(Request(sa["token_uri"],
        data=urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": jwt}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"}))
    return json.loads(resp.read())["access_token"]

def gsc_query(token, site_url, body):
    encoded = site_url.replace('/', '%2F').replace(':', '%3A')
    data = json.dumps(body).encode()
    req = Request(f"https://www.googleapis.com/webmasters/v3/sites/{encoded}/searchAnalytics/query",
        data=data, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    resp = urlopen(req)
    return json.loads(resp.read())

def main():
    token = get_access_token()
    now = time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 2*86400))
    start_date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 30*86400))
    
    sites = [
        ('sinabarimd', 'sc-domain:sinabarimd.com'),
        ('sinabari_net', 'sc-domain:sinabari.net'),
        ('sinabariplasticsurgery', 'sc-domain:sinabariplasticsurgery.com'),
    ]
    
    results = {}
    for site_id, gsc_prop in sites:
        print(f"Querying {site_id}...")
        try:
            queries = gsc_query(token, gsc_prop, {"startDate": start_date, "endDate": end_date, "dimensions": ["query"], "rowLimit": 25})
            pages = gsc_query(token, gsc_prop, {"startDate": start_date, "endDate": end_date, "dimensions": ["page"], "rowLimit": 25})
            branded = gsc_query(token, gsc_prop, {"startDate": start_date, "endDate": end_date, "dimensions": ["query"], "rowLimit": 10,
                "dimensionFilterGroups": [{"filters": [{"dimension": "query", "operator": "contains", "expression": "sina bari"}]}]})
            
            q_rows = queries.get('rows', [])
            p_rows = pages.get('rows', [])
            b_rows = branded.get('rows', [])
            
            results[site_id] = {
                "clicks": sum(r.get('clicks', 0) for r in q_rows),
                "impressions": sum(r.get('impressions', 0) for r in q_rows),
                "top_queries": [{"query": r['keys'][0], "clicks": r['clicks'], "impressions": r['impressions'], "position": round(r['position'], 1)} for r in q_rows[:10]],
                "top_pages": [{"page": r['keys'][0], "clicks": r['clicks'], "impressions": r['impressions'], "position": round(r['position'], 1)} for r in p_rows[:10]],
                "branded_queries": [{"query": r['keys'][0], "clicks": r['clicks'], "impressions": r['impressions'], "position": round(r['position'], 1)} for r in b_rows],
                "indexed_pages": len(p_rows),
                "best_branded_position": min((r['position'] for r in b_rows), default=None),
            }
            print(f"  clicks={results[site_id]['clicks']} imp={results[site_id]['impressions']} branded_pos={results[site_id]['best_branded_position']}")
        except Exception as e:
            print(f"  Error: {e}")
            results[site_id] = {"error": str(e)}
    
    # Push to Measurement Agent
    measurement = {"measured_at": now, "source": "gsc", "sites": results,
        "total_clicks": sum(r.get('clicks', 0) for r in results.values()),
        "total_impressions": sum(r.get('impressions', 0) for r in results.values()),
        "branded_positions": {k: v.get('best_branded_position') for k, v in results.items() if v.get('best_branded_position')}}
    
    payload = json.dumps({"measurement": measurement}).encode()
    req = Request(f"{N8N_WEBHOOK}/store-measurement", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urlopen(req)
        print(f"\nPushed to agent: {resp.read().decode()[:100]}")
    except Exception as e:
        print(f"\nFailed to push (agent may need store-measurement endpoint): {e}")
    
    print(f"\nMeasurement complete: {json.dumps(measurement, indent=2)[:500]}")
    return measurement

if __name__ == '__main__':
    main()
