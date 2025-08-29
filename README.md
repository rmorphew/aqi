# AQI Tools

Small utility scripts for working with U.S. air quality data and ZIP codes.

## Contents

* `epa_aqi_downloader.py` downloads EPA AQI data by pollutant and year. Writes a combined CSV.
* `get_zip_centroids.py` builds an Excel file of ZIP code centroids using Google Maps Geocoding.
* `monitor_zip_matcher.py` assigns each monitoring site to its nearest ZIP centroid.

## Requirements

* Python 3.9 to 3.12
* Dependencies are pinned in `requirements.txt`:

  ```
  pandas==2.2.2
  numpy==2.0.2
  requests==2.32.3
  openpyxl==3.1.5
  ```

## Installation

```bash
# Clone
git clone https://github.com/rmorphew/aqi.git
cd aqi

# Create a virtual environment
python3 -m venv .venv
# macOS or Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## End-to-end workflow

1. Download AQI data.
2. Build ZIP centroids.
3. Match monitors to nearest ZIPs.

```bash
# 1) Download AQI data
python epa_aqi_downloader.py

# Output
# - aqi_data/ per-pollutant CSVs
# - combined_aqi_data.csv at repo root
# - aqi_download.log

# 2) Build ZIP centroids
python get_zip_centroids.py \
  --zips zips.csv \
  --api-key YOUR_GOOGLE_API_KEY \
  --output ZIP_Code_Centroids.xlsx \
  --sleep 0.25

# 3) Match monitors to nearest ZIPs
python monitor_zip_matcher.py \
  ZIP_Code_Centroids.xlsx \
  combined_aqi_data.csv \
  monitors_with_zip.csv
```

### Notes

* `epa_aqi_downloader.py` uses constants at the top of the file. Edit the year range, pollutants, and `COUNTY_CODE` if needed.
* `monitor_zip_matcher.py` expects these columns in the monitors input:

  * `Site ID`, `Local Site Name`, `Site Latitude`, `Site Longitude`, `AQS Parameter Description`
    If your `combined_aqi_data.csv` does not include all of these, provide a monitors CSV from EPA that does.

## Script details

### epa\_aqi\_downloader.py

Downloads daily air quality data from the EPA broker service.

**Key constants (parameters):**

* `BASE_URL`: The EPA broker endpoint used to build requests. Default is `https://www3.epa.gov/cgi-bin/broker`.
* `START_YEAR` / `END_YEAR`: Year range to download. Script will loop across all years in the range.
* `POLLUTANTS`: Dictionary mapping pollutant names to EPA parameter codes. Defaults include `CO`, `Pb`, `NO2`, `Ozone`, `PM10`, `PM2.5`, `SO2`.
* `COUNTY_CODE`: FIPS county code (e.g. `42003` for Allegheny County, PA). Determines which county’s data is retrieved.
* `OUTPUT_DIR`: Directory where individual pollutant/year CSVs are saved (`aqi_data/`).
* `LOG_FILE`: Log file written during execution (`aqi_download.log`).
* `COMBINED_FILE`: Path to the merged CSV containing all pollutants and years (`combined_aqi_data.csv`).

**Operation:**

* Loops over pollutants and years.
* Requests data, extracts the CSV link, downloads, and saves per-pollutant CSVs.
* After all downloads, concatenates all files in `OUTPUT_DIR` into `combined_aqi_data.csv`.

### get\_zip\_centroids.py

* Inputs

  * `--zips` path to a CSV or TXT of ZIP codes. If CSV, the first column is used.
  * `--api-key` Google Maps Geocoding API key.
  * `--output` optional. Default `ZIP_Code_Centroids.xlsx`.
  * `--sleep` optional throttle between requests. Default `0.25` seconds.
* Output

  * Excel file with columns `ZIP Code`, `Latitude`, `Longitude`.

### monitor\_zip\_matcher.py

* Arguments

  * `centroids_file` Excel file from the previous step.
  * `monitors_file` CSV with site coordinates and identifiers.
  * `output_file` path for the enriched CSV.
* Adds columns `Centroid_Zipcode`, `Centroid_Lat`, `Centroid_Lon`, `Distance_to_Centroid`.

## Troubleshooting

* If you see a NumPy or Pandas binary mismatch, you are likely outside the virtual environment. Activate `.venv` and retry.
* Google Maps Geocoding requests can be rate limited. Increase `--sleep` if needed.
* Large CSVs can use a lot of memory. Close other applications if you process big counties or long year ranges.

## Data sources

* EPA Air Quality System broker endpoints.
* Google Maps Geocoding API for ZIP centroids.

## License

MIT License

```
MIT License

Copyright (c) 2025 Morphew Consulting, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Author

Morphew Consulting, LLC
