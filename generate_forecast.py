import xarray as xr
import requests
from datetime import datetime

def download_grib():
    # Bugünün tarihini YYYYMMDD formatında al
    today = datetime.utcnow().strftime('%Y%m%d')
    cycle = '18'  # UTC cycle (00, 06, 12, 18) - isteğe göre değiştirebilirsin
    forecast_hour = 'f000'

    url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{today}/{cycle}/atmos/gfs.t{cycle}z.pgrb2.0p25.{forecast_hour}"
    local_file = "gfs_latest.grib"

    print(f"Downloading GFS file: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_file, "wb") as f:
            f.write(response.content)
        print("Download complete.")
    else:
        raise Exception(f"Failed to download GRIB file, status code: {response.status_code}")

    return local_file

def main():
    grib_file = download_grib()

    # Surface level verilerini aç
    try:
        ds_surface = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'surface'})
        print("Surface level data loaded successfully.")
    except Exception as e:
        print(f"Error opening surface level data: {e}")

    # Atmosphere single layer (örneğin rüzgar gücü için) aç
    try:
        ds_atmos = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'atmosphereSingleLayer'})
        print("Atmosphere single layer data loaded successfully.")
    except Exception as e:
        print(f"Error opening atmosphere single layer data: {e}")

if __name__ == "__main__":
    main()
