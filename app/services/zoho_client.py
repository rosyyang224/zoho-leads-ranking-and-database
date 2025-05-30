import os
import json
import requests
from typing import Dict, List, Optional
import pandas as pd
from app.utils.csv_parser import parse_csv


class ZohoBulkReadClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        api_domain: str = "https://www.zohoapis.com"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.api_domain = api_domain
        self.access_token = self.get_access_token()
        self.base_url = f"{api_domain}/crm/bulk/v8/read"

    def get_access_token(self) -> str:
        """
        Exchange refresh token for an access token.
        """
        url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        response = requests.post(url, data=data)
        response.raise_for_status()

        access_token = response.json().get("access_token")
        if not access_token:
            raise Exception(f"Failed to retrieve access token: {response.text}")

        print("✅ Access token retrieved successfully")
        return access_token

    def create_bulk_read_job(
        self,
        module_name: str,
        fields: Optional[List[str]] = None,
        criteria: Optional[Dict] = None,
        callback_url: Optional[str] = None,
        file_type: str = "csv",
        page: int = 1,
        page_token: Optional[str] = None
    ) -> Dict:
        """
        Create a Zoho CRM Bulk Read job.
        """
        payload = {
            "query": {
                "module": {
                    "api_name": module_name
                }
            }
        }

        if fields and file_type != 'ics':
            payload["query"]["fields"] = fields

        if criteria:
            payload["query"]["criteria"] = criteria

        if page_token:
            payload["query"]["page_token"] = page_token
        else:
            payload["query"]["page"] = page

        if file_type == "ics":
            if module_name != "Events":
                raise ValueError("ICS format only valid for Events module.")
            payload["file_type"] = "ics"

        if callback_url:
            payload["callback"] = {
                "url": callback_url,
                "method": "post"
            }

        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }

        print("📤 Sending bulk read request:")
        print(json.dumps(payload, indent=2))

        response = requests.post(self.base_url, headers=headers, json=payload)

        try:
            response.raise_for_status()
            result = response.json()
            print("📄 Response from Zoho:")
            print(json.dumps(result, indent=2))
            return result
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Raw response:")
            print(response.text)
            return {"error": "Could not parse response", "raw": response.text}
    
    def get_job_status(self, job_id: str) -> Dict:
        url = f"{self.api_domain}/crm/bulk/v8/read/{job_id}"
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
