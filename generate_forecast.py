# generate_forecast.py
from datetime import datetime
import xarray as xr
import numpy as np
import json
import requests

# İskoçya koordinatları
lat_slice = slice(55.5, 58)
lon_slice = slice(-3.5, -1)

def get_gfs_latest_url():
    """
    Güncel GFS 0.25° yüzey verisinin URL'sini oluşturur.
    """
    now = datetime.utcnow()
    YYYYMMDD = now.strftime("%Y%m%d")
    HH = str((now.hour // 6) * 6).zfill(2)  # En yakın 00, 06, 12, 18 saatleri
    forecast_hour = "000"  # Analiz (f000)
    url = (
        f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
        f"gfs.{YYYYMMDD}/{HH}/atmos/gfs.t{HH}z.pgrb2.0p25.f{forecast_hour}"
    )
    return url

def download_grib(local_file="gfs_latest.grib"):
    url = get_gfs_latest_url()
    print(f"Downloading GFS file: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}  # 403 engelini aşmak için
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        with open(local_file, "wb") as f:
            f.write(r.content)
        print("Download complete.")
    else:
        raise Exception(f"Failed to download GRIB file, status code: {r.status_code}")
    return local_file

def process_forecast(grib_file):
    # Surface level verilerini aç
    ds_surface = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'surface'})

    # Rüzgar hızı (u10/v10) kontrolü
    if 'u10' in ds_surface.variables and 'v10' in ds_surface.variables:
        u10 = ds_surface['u10'].sel(latitude=lat_slice, longitude=lon_slice)
        v10 = ds_surface['v10'].sel(latitude=lat_slice, longitude=lon_slice)
        wind = np.sqrt(u10**2 + v10**2)
    else:
        raise KeyError("GRIB içinde u10/v10 bulunamadı!")

    # Kısa dalga radyasyonu (solar)
    solar = ds_surface.get('dswrf', ds_surface.get('ssr'))
    if solar is None:
        raise KeyError("GRIB içinde kısa dalga radyasyonu bulunamadı!")
    solar = solar.sel(latitude=lat_slice, longitude=lon_slice)

    # Basit MW dönüşümü (örnek)
    windMW = [int(np.mean(wind.isel(time=i).values)*100) for i in range(min(5, wind.sizes['time']))]
    solarMW = [int(np.mean(solar.isel(time=i).values)/10) for i in range(min(5, solar.sizes['time']))]

    # JSON kaydı
    forecast = {
        "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "windMW": windMW,
        "solarMW": solarMW
    }

    with open('data/scotland_forecast.json', 'w') as f:
        json.dump(forecast, f)

    print("Forecast JSON saved.")

def main():
    grib_file = download_grib()
    process_forecast(grib_file)

if __name__ == "__main__":
    main()
