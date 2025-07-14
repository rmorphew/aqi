import argparse
import pandas as pd
import requests
import time
import os
import sys

def load_zip_codes(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(file_path)
        zip_codes = df.iloc[:, 0].astype(str).str.zfill(5).tolist()
    else:
        with open(file_path, 'r') as f:
            zip_codes = [line.strip().zfill(5) for line in f if line.strip()]
    return zip_codes

def get_coordinates(zip_code, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&components=country:US&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None

def main():
    parser = argparse.ArgumentParser(description="Get ZIP code centroids from Google Maps Geocoding API.")
    parser.add_argument("--zips", required=True, help="Path to file with ZIP codes (CSV or TXT, 1 ZIP per line)")
    parser.add_argument("--api-key", required=True, help="Google Maps Geocoding API key")
    parser.add_argument("--output", default="ZIP_Code_Centroids.xlsx", help="Output Excel filename")
    parser.add_argument("--sleep", type=float, default=0.25, help="Delay between API requests (in seconds)")
    args = parser.parse_args()

    zip_codes = load_zip_codes(args.zips)
    print(f"Loaded {len(zip_codes)} ZIP codes from {args.zips}")

    if os.path.exists(args.output):
        df_existing = pd.read_excel(args.output)
        processed = set(df_existing["ZIP Code"].astype(str))
        print(f"Found {len(processed)} previously processed ZIPs in {args.output}")
    else:
        df_existing = pd.DataFrame(columns=["ZIP Code", "Latitude", "Longitude"])
        processed = set()

    new_results = []
    for i, zip_code in enumerate(zip_codes, 1):
        if zip_code in processed:
            print(f"[{i}/{len(zip_codes)}] Skipping {zip_code} (already processed)")
            continue

        print(f"[{i}/{len(zip_codes)}] Processing {zip_code}...", end=" ")
        lat, lon = get_coordinates(zip_code, args.api_key)
        if lat is not None:
            print(f"→ {lat:.5f}, {lon:.5f}")
        else:
            print("→ Failed")
        new_results.append({"ZIP Code": zip_code, "Latitude": lat, "Longitude": lon})
        time.sleep(args.sleep)

        # Save in batches
        if i % 10 == 0 or i == len(zip_codes):
            combined = pd.concat([df_existing, pd.DataFrame(new_results)], ignore_index=True)
            combined.to_excel(args.output, index=False)
            df_existing = combined
            new_results = []
            print(f"  → Saved progress to {args.output}")

    print("Done.")

if __name__ == "__main__":
    main()
