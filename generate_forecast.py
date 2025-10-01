import requests
import xarray as xr
import numpy as np
import json
import os
from datetime import datetime

# --- GRIB İndirme Fonksiyonu ---
def download_grib():
    today = datetime.utcnow().strftime('%Y%m%d')
    cycle = '18'  # UTC cycle: 00, 06, 12, 18
    forecast_hour = 'f000'

    url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{today}/{cycle}/atmos/gfs.t{cycle}z.pgrb2.0p25.{forecast_hour}"
    local_file = "gfs_latest.grib"

    print(f"Downloading GFS file: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(local_file, "wb") as f:
            f.write(response.content)
        print("Download complete.")
    else:
        raise Exception(f"Failed to download GRIB file, status code: {response.status_code}")

    return local_file

# --- GFS verilerini aç ve İskoçya slice al ---
def open_grib(file_path):
    try:
        ds_surface = xr.open_dataset(file_path, engine='cfgrib', filter_by_keys={'typeOfLevel': 'surface'})
        print("Surface level data loaded.")
        return ds_surface
    except Exception as e_surface:
        print(f"Surface level açılırken hata: {e_surface}")
        # fallback
        try:
            ds_atmos = xr.open_dataset(file_path, engine='cfgrib', filter_by_keys={'typeOfLevel': 'atmosphereSingleLayer'})
            print("Atmosphere single layer data loaded.")
            return ds_atmos
        except Exception as e_atmos:
            raise RuntimeError(f"GRIB açılırken hata: Surface:{e_surface} | Atmosphere:{e_atmos}")

# --- MW hesaplama ve JSON kaydetme ---
def generate_forecast(ds):
    lat_slice = slice(55.5, 58)
    lon_slice = slice(-3.5, -1)

    # Rüzgar ve güneş verileri
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
    print("Forecast JSON kaydedildi.")

# --- Price & Volume Örneği ---
def generate_price_volume():
    price = [50, 48, 46, 52, 49]
    volume = [400, 380, 420, 390, 410]

    pv = {
        "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "price": price,
        "volume": volume
    }

    with open('data/price_volume.json', 'w') as f:
        json.dump(pv, f)
    print("Price/Volume JSON kaydedildi.")

# --- Main ---
def main():
    grib_file = download_grib()
    ds = open_grib(grib_file)
    generate_forecast(ds)
    generate_price_volume()

if __name__ == "__main__":
    main()
