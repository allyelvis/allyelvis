#!/usr/bin/env python3
import os, json, datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_gcp_metrics():
    sa_json = os.getenv("GCP_SERVICE_ACCOUNT")
    if not sa_json:
        return {
            "GCP_PROJECT_COUNT": "0",
            "GCP_VM_COUNT": "0",
            "FIREBASE_APPS": "0",
            "LATEST_DEPLOYMENT_DATE": "N/A",
            "GCP_CPU_USAGE": "N/A",
            "GCP_MEMORY_USAGE": "N/A",
            "GCP_NETWORK_HEALTH": "N/A",
            "GCP_UPTIME": "N/A",
            "TIMESTAMP": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        }
    creds = service_account.Credentials.from_service_account_info(
        json.loads(sa_json),
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    crm = build("cloudresourcemanager", "v1", credentials=creds)
    compute = build("compute", "v1", credentials=creds)
    firebase = build("firebase", "v1beta1", credentials=creds)

    try:
        projects_resp = crm.projects().list().execute()
        projects = projects_resp.get("projects", []) if projects_resp else []
    except HttpError:
        projects = []
    project_count = len(projects)

    vm_count = 0
    for p in projects:
        pid = p.get("projectId")
        if not pid: continue
        try:
            vms = compute.instances().aggregatedList(project=pid).execute()
            items = vms.get("items", {})
            for _, data in items.items():
                if "instances" in data:
                    vm_count += len(data["instances"])
        except HttpError:
            continue

    firebase_count = 0
    try:
        fb_resp = firebase.projects().list().execute()
        for item in fb_resp.get("results", []):
            firebase_count += 1
    except HttpError:
        firebase_count = "N/A"

    return {
        "GCP_PROJECT_COUNT": project_count,
        "GCP_VM_COUNT": vm_count,
        "FIREBASE_APPS": firebase_count,
        "LATEST_DEPLOYMENT_DATE": "N/A",
        "GCP_CPU_USAGE": "N/A",
        "GCP_MEMORY_USAGE": "N/A",
        "GCP_NETWORK_HEALTH": "N/A",
        "GCP_UPTIME": "N/A",
        "TIMESTAMP": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    }

def update_readme(metrics, readme_path="README.md"):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    for k,v in metrics.items():
        content = content.replace(f"{{{{{k}}}}}", str(v))
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    metrics = get_gcp_metrics()
    update_readme(metrics)
