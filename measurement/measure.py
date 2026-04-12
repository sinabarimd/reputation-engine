#!/usr/bin/env python3
"""
Reputation Engine — Google Search Console Data Collection

Collects search performance data from GSC for all four domains
and pushes it to the Measurement Agent workflow via webhook.

Uses a service account for authentication (no interactive OAuth).

Usage:
    python measure.py

Environment:
    GSC_SERVICE_ACCOUNT_FILE — path to service account JSON key
    N8N_WEBHOOK_URL          — webhook endpoint for data push
"""

import json
import os
import sys
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SERVICE_ACCOUNT_FILE = os.environ.get(
    "GSC_SERVICE_ACCOUNT_FILE", "/etc/reputation-engine/gsc-service-account.json"
)
WEBHOOK_URL = os.environ.get(
    "N8N_WEBHOOK_URL", "http://localhost:5678/webhook/store-measurement"
)

# All four domains to monitor
SITES = [
    "sc-domain:sinabarimd.com",
    "sc-domain:sinabari.net",
    "sc-domain:drsinabari.com",
    "sc-domain:sinabariplasticsurgery.com",
]

# Branded query patterns to track
BRANDED_QUERIES = [
    "sina bari",
    "sina bari md",
    "dr sina bari",
    "sinabari",
    "sinabarimd",
]

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


# ---------------------------------------------------------------------------
# GSC Client
# ---------------------------------------------------------------------------

def get_gsc_service():
    """Build authenticated GSC service client."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("searchconsole", "v1", credentials=credentials)


def fetch_search_analytics(service, site_url, start_date, end_date):
    """
    Fetch search analytics for a site over a date range.
    Returns per-query performance data.
    """
    request_body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query", "page"],
        "rowLimit": 1000,
        "dimensionFilterGroups": [
            {
                "filters": [
                    {
                        "dimension": "query",
                        "operator": "contains",
                        "expression": "sina bari",
                    }
                ]
            }
        ],
    }

    response = (
        service.searchanalytics()
        .query(siteUrl=site_url, body=request_body)
        .execute()
    )

    return response.get("rows", [])


def fetch_branded_performance(service, site_url, start_date, end_date):
    """Fetch aggregate branded query performance."""
    results = []
    for query in BRANDED_QUERIES:
        request_body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "dimensionFilterGroups": [
                {
                    "filters": [
                        {
                            "dimension": "query",
                            "operator": "equals",
                            "expression": query,
                        }
                    ]
                }
            ],
        }
        response = (
            service.searchanalytics()
            .query(siteUrl=site_url, body=request_body)
            .execute()
        )
        rows = response.get("rows", [])
        if rows:
            results.append(
                {
                    "query": query,
                    "clicks": rows[0].get("clicks", 0),
                    "impressions": rows[0].get("impressions", 0),
                    "ctr": rows[0].get("ctr", 0),
                    "position": rows[0].get("position", 0),
                }
            )

    return results


# ---------------------------------------------------------------------------
# Data Push
# ---------------------------------------------------------------------------

def push_to_n8n(data):
    """Push collected data to the Measurement Agent webhook."""
    import urllib.request

    payload = json.dumps(
        {
            "source": "gsc",
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "data": data,
        }
    ).encode()

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"[{datetime.now().isoformat()}] Starting GSC data collection")

    service = get_gsc_service()

    # Collect last 7 days of data
    end_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")  # GSC has ~3 day lag
    start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

    all_data = {}

    for site_url in SITES:
        domain = site_url.replace("sc-domain:", "")
        print(f"  Fetching data for {domain}...")

        try:
            analytics = fetch_search_analytics(service, site_url, start_date, end_date)
            branded = fetch_branded_performance(service, site_url, start_date, end_date)

            all_data[domain] = {
                "search_analytics": analytics,
                "branded_performance": branded,
                "period": {"start": start_date, "end": end_date},
            }

            print(f"    {len(analytics)} rows, {len(branded)} branded queries tracked")

        except Exception as e:
            print(f"    Error: {e}")
            all_data[domain] = {"error": str(e)}

    # Push to n8n
    try:
        result = push_to_n8n(all_data)
        print(f"  Data pushed to n8n: {result}")
    except Exception as e:
        print(f"  Failed to push to n8n: {e}")
        # Save locally as fallback
        fallback_path = f"/tmp/gsc_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(fallback_path, "w") as f:
            json.dump(all_data, f, indent=2)
        print(f"  Saved locally to {fallback_path}")

    print(f"[{datetime.now().isoformat()}] Collection complete")


if __name__ == "__main__":
    main()
