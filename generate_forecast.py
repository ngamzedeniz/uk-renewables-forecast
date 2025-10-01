import requests
import xarray as xr
import numpy as np
import json
from datetime import datetime

# --- GRIB indirme fonksiyonu ---
def download_grib():
    today = datetime.utcnow().strftime('%Y%m%d')
    cycle = '18'  # 00, 06, 12, 18 UTC seçenekleri
    forecast_hour = 'f000'

    url = f"https://tgftp.nws.noaa.gov/data/nccf/com/gfs/prod/gfs.{today}/{cycle}/atmos/gfs.t{cycle}z.pgrb2.0p25.{forecast_hour}"
    local_file = "data/gfs_latest.grib"

    headers = {"User-Agent": "Mozilla/5.0 (compatible; GFS downloader)"}
    print(f"Downloading GFS file: {url}")

    r = requests.get(url, headers=headers, stream=True)
    if r.status_code == 200:
        with open(local_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("Download complete.")
    else:
        raise Exception(f"Failed to download GRIB file, status code: {r.status_code}")

    return local_file

# --- GFS verisini aç ve İskoçya verilerini işle ---
def process_grib(grib_file):
    lat_slice = slice(55.5, 58)
    lon_slice = slice(-3.5, -1)

    try:
        ds_surface = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'surface'})
        wind = ds_surface['10m_u_component_of_wind'].sel(latitude=lat_slice, longitude=lon_slice)
        solar = ds_surface['surface_downwelling_shortwave_radiation'].sel(latitude=lat_slice, longitude=lon_slice)
    except Exception as e:
        print(f"Error opening surface level data: {e}")
        return None

    # Basit MW dönüşümü
    windMW = [int(np.mean(wind.isel(time=i).values) * 100) for i in range(5)]
    solarMW = [int(np.mean(solar.isel(time=i).values) / 10) for i in range(5)]

    forecast = {
        "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "windMW": windMW,
        "solarMW": solarMW
    }

    with open('data/scotland_forecast.json', 'w') as f:
        json.dump(forecast, f)

    print("Forecast JSON created successfully.")
    return forecast

# --- Ana fonksiyon ---
def main():
    grib_file = download_grib()
    process_grib(grib_file)

if __name__ == "__main__":
    main()
