# generate_forecast.py
import requests
import xarray as xr
import numpy as np
import json
from datetime import datetime

# --- GFS 0.25° URL ---
def get_gfs_latest_url():
    now = datetime.utcnow()
    YYYYMMDD = now.strftime("%Y%m%d")
    HH = str((now.hour // 6) * 6).zfill(2)
    forecast_hour = "000"  # analiz saatinde
    url = (
        f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
        f"gfs.{YYYYMMDD}/{HH}/atmos/gfs.t{HH}z.pgrb2.0p25.f{forecast_hour}"
    )
    return url

# --- GFS dosyasını indir ---
def download_grib():
    url = get_gfs_latest_url()
    local_file = "./data/gfs_latest.grib"
    print(f"Downloading GFS file: {url}")
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open(local_file, "wb") as f:
            f.write(r.content)
        print("Download complete.")
    else:
        raise Exception(f"Failed to download GRIB file, status code: {r.status_code}")
    return local_file

# --- Forecast hesapla ve JSON kaydet ---
def process_forecast(grib_file):
    # Surface level verileri (rüzgar ve güneş)
    ds_surface = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'surface'})

    # İskoçya koordinatları
    lat_slice = slice(55.5, 58)
    lon_slice = slice(-3.5, -1)

    # 10m rüzgar ve kısa dalga radyasyonu
    wind = ds_surface['10m_u_component_of_wind'].sel(latitude=lat_slice, longitude=lon_slice)
    solar = ds_surface['surface_downwelling_shortwave_radiation'].sel(latitude=lat_slice, longitude=lon_slice)

    # Basit MW dönüşümü
    windMW = [int(np.mean(wind.isel(time=i).values)*100) for i in range(min(5, len(wind.time)))]
    solarMW = [int(np.mean(solar.isel(time=i).values)/10) for i in range(min(5, len(solar.time)))]

    forecast = {
        "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "windMW": windMW,
        "solarMW": solarMW
    }

    with open('data/scotland_forecast.json', 'w') as f:
        json.dump(forecast, f)
    print("Forecast JSON saved.")

# --- Örnek Elexon fiyat & hacim (doldur) ---
def process_price_volume():
    # Burada gerçek API çekilebilir
    price = [50, 48, 46, 52, 49]
    volume = [400, 380, 420, 390, 410]

    pv = {
        "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "price": price,
        "volume": volume
    }

    with open('data/price_volume.json', 'w') as f:
        json.dump(pv, f)
    print("Price/Volume JSON saved.")

def main():
    grib_file = download_grib()
    process_forecast(grib_file)
    process_price_volume()

if __name__ == "__main__":
    main()
