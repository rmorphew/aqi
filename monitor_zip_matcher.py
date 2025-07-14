import pandas as pd
import math
import sys

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points 
    on the Earth specified by latitude and longitude using the Haversine formula.
    """
    R = 3958.8  # Radius of Earth in miles
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def assign_nearest_centroid(centroids_file, monitors_file, output_file):
    print("Loading ZIP Code centroids file...")
    centroids_df = pd.read_excel(centroids_file)
    print(f"Loaded {len(centroids_df)} centroids.")
    
    # Ensure necessary columns exist
    required_centroid_cols = {"ZIP Code", "Latitude", "Longitude"}
    if not required_centroid_cols.issubset(centroids_df.columns):
        raise ValueError("The centroids file must contain 'ZIP Code', 'Latitude', and 'Longitude' columns.")
    
    print("Loading monitors data file...")
    monitors_df = pd.read_csv(monitors_file, low_memory=False)
    print(f"Loaded {len(monitors_df)} monitor sites.")
    
    # Ensure necessary columns exist
    required_monitor_cols = {"Site Latitude", "Site Longitude", "Site ID", "Local Site Name", "AQS Parameter Description"}
    if not required_monitor_cols.issubset(monitors_df.columns):
        raise ValueError("The monitors file must contain 'Site Latitude', 'Site Longitude', 'Site ID', 'Local Site Name', and 'AQS Parameter Description' columns.")
    
    # Cache for previously computed nearest centroids
    cache = {}

    # Function to find the nearest centroid
    def find_nearest_centroid(site_lat, site_lon):
        min_distance = float("inf")
        nearest_zip, nearest_lat, nearest_lon = None, None, None
        
        for _, centroid in centroids_df.iterrows():
            zip_code, cent_lat, cent_lon = centroid["ZIP Code"], centroid["Latitude"], centroid["Longitude"]
            distance = haversine(site_lat, site_lon, cent_lat, cent_lon)
            
            if distance < min_distance:
                min_distance = distance
                nearest_zip, nearest_lat, nearest_lon = zip_code, cent_lat, cent_lon
        
        return nearest_zip, nearest_lat, nearest_lon, min_distance
    
    print("Processing monitor sites...")
    nearest_centroids = []
    for idx, row in monitors_df.iterrows():
        cache_key = (row["Site ID"], row["Local Site Name"], row["AQS Parameter Description"], row["Site Latitude"], row["Site Longitude"])
        
        if cache_key in cache:
            nearest_centroids.append(cache[cache_key])
        else:
            nearest = find_nearest_centroid(row["Site Latitude"], row["Site Longitude"])
            cache[cache_key] = nearest
            nearest_centroids.append(nearest)
        
        if idx % 100 == 0:
            print(f"Processed {idx} monitor sites...")
    
    # Convert results into separate columns
    monitors_df["Centroid_Zipcode"], monitors_df["Centroid_Lat"], monitors_df["Centroid_Long"], monitors_df["Distance_to_Centroid"] = zip(*nearest_centroids)
    
    print("Saving updated monitors data...")
    monitors_df.to_csv(output_file, index=False)
    print(f"Updated monitors data saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <centroids_file> <monitors_file> <output_file>")
        sys.exit(1)
    
    centroids_file = sys.argv[1]
    monitors_file = sys.argv[2]
    output_file = sys.argv[3]
    
    assign_nearest_centroid(centroids_file, monitors_file, output_file)
