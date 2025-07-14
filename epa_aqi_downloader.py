import requests
import os
import re
import pandas as pd

# Constants
BASE_URL = "https://www3.epa.gov/cgi-bin/broker"
START_YEAR = 2016
END_YEAR = 2016
POLLUTANTS = {
    "CO": "42101",
    "Pb": "12128%27%2C%2714129%27%2C%2785129",
    "NO2": "42602",
    "Ozone": "44201",
    "PM10": "81102",
    "PM2.5": "88101%27%2C%2788502",
    "SO2": "42401"
}
COUNTY_CODE = "42003"  # Allegheny County
OUTPUT_DIR = "aqi_data"
LOG_FILE = "aqi_download.log"
COMBINED_FILE = "combined_aqi_data.csv"

# Helper functions
def log_message(message):
    """Log messages to a file and print to console."""
    print(message)
    with open(LOG_FILE, "a") as log:
        log.write(message + "\n")

def clear_log():
    """Clear the log file."""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

def extract_download_link(response_text):
    """Extract the download link from the response text."""
    match = re.search(r'href="(https://www3\.epa\.gov[^"]+)"', response_text)
    return match.group(1) if match else None

def fetch_data(url):
    """Fetch data from the URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        log_message(f"Failed to fetch data from {url}: {response.status_code}")
        return None

def download_data(pollutant_code, year):
    """Download data for a given pollutant and year."""
    url = f"{BASE_URL}?_service=data&_debug=0&_program=dataprog.ad_data_daily_airnow_method.sas&poll={pollutant_code}&year={year}&state=-1&cbsa=-1&county={COUNTY_CODE}&site=-1"
    log_message(f"Fetching data from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        download_link = extract_download_link(response.text)
        if download_link:
            log_message(f"Found download link: {download_link}")
            return fetch_data(download_link)
        else:
            log_message(f"No download link found for {pollutant_code}, year {year}")
    else:
        log_message(f"Failed to fetch data for {pollutant_code}, year {year}: {response.status_code}")
    return None

def save_data(pollutant, year, data):
    """Save data to a CSV file."""
    filename = os.path.join(OUTPUT_DIR, f"{pollutant}_{year}.csv")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(filename, "w") as file:
        file.write(data)
    log_message(f"Saved data for {pollutant}, year {year} to {filename}")

def combine_files():
    """Combine all CSV files into one file."""
    combined_data = []
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".csv"):
            file_path = os.path.join(OUTPUT_DIR, file)
            try:
                data = pd.read_csv(file_path)
                combined_data.append(data)
            except Exception as e:
                log_message(f"Failed to read file {file}: {e}")
    if combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)
        combined_df.to_csv(COMBINED_FILE, index=False)
        log_message(f"Combined data saved to {COMBINED_FILE}")
    else:
        log_message("No files to combine.")

# Main process
def main():
    clear_log()
    for pollutant, code in POLLUTANTS.items():
        log_message(f"Processing pollutant: {pollutant}")
        for year in range(START_YEAR, END_YEAR + 1):
            log_message(f"Fetching data for year {year}")
            data = download_data(code, year)
            if data:
                save_data(pollutant, year, data)
    combine_files()

if __name__ == "__main__":
    main()
