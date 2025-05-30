import os
import time
import requests
import pandas as pd
from app.services.zoho_client import ZohoBulkReadClient
from app.utils.csv_parser import parse_csv
import zipfile
from io import BytesIO

def sync_and_process_zoho_leads():
    print("\n🚀 Starting Zoho Bulk Read Sync...")

    client = ZohoBulkReadClient(
        client_id=os.getenv("ZOHO_SERVER_CLIENT_ID"),
        client_secret=os.getenv("ZOHO_SERVER_CLIENT_SECRET"),
        refresh_token=os.getenv("ZOHO_SERVER_REFRESH")
    )
    # Step 1: Create Bulk Read Job
    response = client.create_bulk_read_job(
        module_name="Leads",
        fields=[]
    )

    headers = {
        "Authorization": f"Zoho-oauthtoken {client.access_token}"
    }
    test = requests.get(
        "https://www.zohoapis.com/crm/v2/Leads",
        headers=headers
    )
    print("📦 Raw response status:", test.status_code)
    print("📦 Raw response text:", test.text)

    try:
        print("📄 Parsed JSON:", test.json())
    except Exception as e:
        print("❌ Failed to parse JSON:", e)


    try:
        job_id = response["data"][0]["details"]["id"]
        print(f"✅ Bulk read job created. Job ID: {job_id}")
    except (KeyError, IndexError):
        print("❌ Failed to create job or extract job ID.")
        return

    # Step 2: Poll for Completion
    download_url = None
    for attempt in range(10):
        status = client.get_job_status(job_id)
        state = status.get("data", [{}])[0].get("state")
        print(f"⏳ Attempt {attempt + 1}: Job state = {state}")

        if state == "COMPLETED":
            download_url = status["data"][0]["result"]["download_url"]
            full_download_url = f"https://www.zohoapis.com{download_url}"
            break
        elif state in ("FAILED", "CANCELLED"):
            print("❌ Job failed or was cancelled.")
            return
        time.sleep(5)

    if not download_url:
        print("❌ Job did not complete in time.")
        return

    # Step 3: Download the CSV
    print(f"⬇️ Downloading CSV from: {full_download_url}")
    headers = {
        "Authorization": f"Zoho-oauthtoken {client.access_token}"
    }
    download_response = requests.get(full_download_url, headers=headers)
    
    if download_response.status_code != 200:
        print(f"❌ Failed to download CSV. Status: {download_response.status_code}")
        print(download_response.text)
        return  # Or raise Exception

    with zipfile.ZipFile(BytesIO(download_response.content)) as z:
        z.extractall(path="leads_data")
        extracted_files = z.namelist()
        print(f"✅ Extracted files: {extracted_files}")

    # # Optional sanity check: make sure it starts with column headers
    # first_line = download_response.content.decode(errors='ignore').splitlines()[0]
    # print(f"🧪 First line of CSV: {first_line}")

    # # Step 4: Parse and Clean
    # df = pd.read_csv(extracted_file_name)
    # cleaned = parse_csv(df)
    # local_clean_path = "leads_cleaned.csv"
    # cleaned.to_csv(local_clean_path, index=False)
    # print(f"✅ Cleaned CSV saved to {local_clean_path}")

    # csv_files = [f for f in extracted_files if f.endswith(".csv")]
    # dfs = [pd.read_csv(os.path.join("leads_data", f)) for f in csv_files]
    # df = pd.concat(dfs, ignore_index=True)
    # cleaned = parse_csv(df)
    # cleaned.to_csv("leads_cleaned.csv", index=False)
