import requests
import os

from dotenv import load_dotenv

load_dotenv()

def get_public_ip():
    """Fetch the public IP address of the home network."""
    response = requests.get("https://icanhazip.com")
    response.raise_for_status()
    return response.text

def get_dns_record(cloudflare_api_url, headers, zone_id, record_name):
    """Retrieve the DNS record from Cloudflare."""
    url = f"{cloudflare_api_url}/zones/{zone_id}/dns_records"
    params = {"type": "A", "name": record_name}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    records = response.json().get("result", [])
    return records[0] if records else None

def update_dns_record(cloudflare_api_url, headers, zone_id, record_id, record_name, ip):
    """Update the DNS record with the new IP address."""
    url = f"{cloudflare_api_url}/zones/{zone_id}/dns_records/{record_id}"
    data = {
        "type": "A",
        "name": record_name,
        "content": ip,
        "ttl": 1,  # Automatic TTL
        "proxied": True
    }
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    # Cloudflare API credentials
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")
    RECORD_NAME = os.getenv("CLOUDFLARE_RECORD_NAME")

    if not CLOUDFLARE_API_TOKEN or not ZONE_ID or not RECORD_NAME:
        print("Error: Please set CLOUDFLARE_API_TOKEN, CLOUDFLARE_ZONE_ID, and CLOUDFLARE_RECORD_NAME as environment variables.")
        return

    cloudflare_api_url = "https://api.cloudflare.com/client/v4"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        current_ip = get_public_ip()
        print(f"Current public IP: {current_ip}")

        dns_record = get_dns_record(cloudflare_api_url, headers, ZONE_ID, RECORD_NAME)

        if dns_record:
            print(f"Found DNS record: {dns_record}")
            if dns_record.get("content") != current_ip:
                print("IP has changed, updating DNS record...")
                update_dns_record(
                    cloudflare_api_url,
                    headers,
                    ZONE_ID,
                    dns_record["id"],
                    RECORD_NAME,
                    current_ip
                )
                print("DNS record updated successfully.")
            else:
                print("IP has not changed, no update required.")
        else:
            print("DNS record not found, please ensure the record exists in Cloudflare.")

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
