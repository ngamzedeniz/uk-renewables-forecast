import xarray as xr
import requests
import numpy as np
import json
from datetime import datetime
import os

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

def process_forecast(grib_file):
    # Önce surface level
    try:
        ds = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'surface'})
        print("Surface level data loaded.")
    except Exception as e1:
        print("Surface level açılmazsa fallback 'atmosphereSingleLayer'...")
        try:
            ds = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'atmosphereSingleLayer'})
            print("Atmosphere single layer data loaded.")
        except Exception as e2:
            raise RuntimeError(f"GRIB açılırken hata: {e1}\n{e2}")

    # İskoçya koordinatları
    lat_slice = slice(55.5, 58)
    lon_slice = slice(-3.5, -1)

    # Rüzgar ve güneş radyasyonu verilerini al
    wind = ds['10m_u_component_of_wind'].sel(latitude=lat_slice, longitude=lon_slice)
    solar = ds['surface_downwelling_shortwave_radiation'].sel(latitude=lat_slice, longitude=lon_slice)

    # Basit MW dönüşümü
    windMW = [int(np.mean(wind.isel(time=i).values)*100) for i in range(min(5, len(wind.time)))]
    solarMW = [int(np.mean(solar.isel(time=i).values)/10) for i in range(min(5, len(solar.time)))]

    forecast = {
        "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "windMW": windMW,
        "solarMW": solarMW
    }

    os.makedirs("data", exist_ok=True)
    with open('data/scotland_forecast.json', 'w') as f:
        json.dump(forecast, f)

    print("Forecast JSON oluşturuldu.")

def main():
    grib_file = download_grib()
    process_forecast(grib_file)

if __name__ == "__main__":
    main()
