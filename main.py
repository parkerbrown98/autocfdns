import requests
import os
import json

from dotenv import load_dotenv

load_dotenv()

def get_public_ip():
    """Fetch the public IP address of the home network."""
    response = requests.get("https://icanhazip.com")
    response.raise_for_status()
    return response.text.strip()

def parse_record_names(raw_record_names):
    """Parse record names from comma-separated string or JSON array."""
    if not raw_record_names:
        return []

    value = raw_record_names.strip()
    if not value:
        return []

    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(name).strip() for name in parsed if str(name).strip()]
        except json.JSONDecodeError:
            pass

    return [name.strip() for name in value.split(",") if name.strip()]

def get_dns_record(cloudflare_api_url, headers, zone_id, record_names):
    """Retrieve DNS records from Cloudflare for all requested names."""
    url = f"{cloudflare_api_url}/zones/{zone_id}/dns_records"
    dns_records = {}

    for record_name in record_names:
        params = {"type": "A", "name": record_name}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            records = response.json().get("result", [])
            dns_records[record_name] = records[0] if records else None
        except requests.RequestException as e:
            print(f"Failed to retrieve DNS record '{record_name}': {e}")
            dns_records[record_name] = None

    return dns_records

def update_dns_record(cloudflare_api_url, headers, zone_id, dns_records, ip):
    """Update each DNS record with the new IP address when needed."""
    for record_name, dns_record in dns_records.items():
        if not dns_record:
            print(f"DNS record '{record_name}' not found, please ensure the record exists in Cloudflare.")
            continue

        if dns_record.get("content") == ip:
            print(f"IP has not changed for '{record_name}', no update required.")
            continue

        print(f"IP has changed for '{record_name}', updating DNS record...")
        url = f"{cloudflare_api_url}/zones/{zone_id}/dns_records/{dns_record['id']}"
        data = {
            "type": "A",
            "name": record_name,
            "content": ip,
            "ttl": 1,  # Automatic TTL
            "proxied": dns_record.get("proxied", True)
        }

        try:
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"DNS record '{record_name}' updated successfully.")
        except requests.RequestException as e:
            print(f"Failed to update DNS record '{record_name}': {e}")

def main():
    # Cloudflare API credentials
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")
    RECORDS_VALUE = os.getenv("CLOUDFLARE_RECORD_NAMES", os.getenv("CLOUDFLARE_RECORD_NAME"))
    RECORD_NAMES = parse_record_names(RECORDS_VALUE)

    if not CLOUDFLARE_API_TOKEN or not ZONE_ID or not RECORD_NAMES:
        print(
            "Error: Please set CLOUDFLARE_API_TOKEN, CLOUDFLARE_ZONE_ID, and "
            "CLOUDFLARE_RECORD_NAME (or CLOUDFLARE_RECORD_NAMES) as environment variables."
        )
        return

    cloudflare_api_url = "https://api.cloudflare.com/client/v4"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        current_ip = get_public_ip()
        print(f"Current public IP: {current_ip}")

        dns_records = get_dns_record(cloudflare_api_url, headers, ZONE_ID, RECORD_NAMES)
        update_dns_record(cloudflare_api_url, headers, ZONE_ID, dns_records, current_ip)

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
