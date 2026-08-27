# Dynamic DNS Updater with Cloudflare API

This Python script updates one or more Cloudflare DNS records with the current public IP address of your home network. It's useful for maintaining dynamic DNS (DDNS) functionality.

## Features

- Fetch the public IP address of your home network using the [ipify API](https://www.ipify.org/).
- Retrieve current DNS records from Cloudflare.
- Update each DNS record if the IP address has changed.

## Prerequisites

- A Cloudflare account with a configured domain.
- An API token with the following permissions:
  - Zone: Read
  - DNS: Edit

## Dependencies

- Python 3.7+
- [requests](https://pypi.org/project/requests/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/parkerbrown98/autocfdns.git
   cd autocfdns
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   Create a `.env` file in the project directory with the following contents:

   ```env
   CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
   CLOUDFLARE_ZONE_ID=your_zone_id
   CLOUDFLARE_RECORD_NAME=your_record_name
   ```

   Replace `your_cloudflare_api_token`, `your_zone_id`, and `your_record_name` with your actual Cloudflare credentials and record information.

   You can also configure multiple records using `CLOUDFLARE_RECORD_NAMES`:

   ```env
   CLOUDFLARE_RECORD_NAMES=sub1.example.com,sub2.example.com
   ```

   Or as a JSON array:

   ```env
   CLOUDFLARE_RECORD_NAMES=["sub1.example.com","sub2.example.com"]
   ```

   `CLOUDFLARE_RECORD_NAME` (single record) is still supported for backward compatibility.

4. **Run the script:**

   ```bash
   python main.py
   ```

## Automating with Crontab

To ensure the script runs periodically and updates your DNS record automatically, you can set it up with `cron`.

### Example Cron Setup

1. **Edit the crontab:**

   Open the crontab editor with the following command:

   ```bash
   crontab -e
   ```

2. **Add a cron job:**

   Add the following line to schedule the script to run every 10 minutes:

   ```bash
   */10 * * * * /usr/bin/env bash -c 'source /path/to/your/project/.env && python3 /path/to/your/project/main.py' >> /path/to/your/project/log.txt 2>&1
   ```

   - Replace `/path/to/your/project/` with the absolute path to your project directory.
   - Redirected output (`>> /path/to/your/project/log.txt`) ensures that logs are saved for debugging.

3. **Save and exit:**

   Save the file and exit the editor. Your cron job is now scheduled.

### Verify the Cron Job

You can check the cron log to ensure the job runs successfully:

```bash
grep CRON /var/log/syslog
```

## Usage

1. **Public IP Detection:**  
   The script fetches your current public IP address using the `ipify` API.

2. **DNS Record Retrieval:**  
   It checks for existing DNS records in Cloudflare matching the configured record name(s).

3. **DNS Record Update:**  
   If the public IP address differs from a record's current value, the script updates that record with the new IP.

4. **Logs:**  
   The script prints information about its progress and any errors encountered.

## Error Handling

- If required environment variables are missing, the script will exit with an error message.
- Network or API issues are caught and logged with a descriptive error message.

## Notes

- Ensure your `CLOUDFLARE_API_TOKEN` is kept secure. Do not share or expose it.
- The script uses a TTL of `1` (automatic) and enables proxying (`proxied: true`) for the DNS record. Adjust this as necessary in the `update_dns_record` function.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for feedback or enhancements.