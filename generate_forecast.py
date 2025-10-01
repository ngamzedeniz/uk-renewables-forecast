import requests
import xarray as xr
import numpy as np
import json
import os

# --- Güncel GFS URL (İskoçya için 0.25° latest) ---
GFS_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.0p25/latest/gfs.t00z.pgrb2.0p25.f000"

# --- GRIB dosyasını indir ---
grib_file = "gfs_latest.grib"
if not os.path.exists(grib_file) or os.path.getsize(grib_file) == 0:
    print("Downloading latest GFS GRIB...")
    r = requests.get(GFS_URL, stream=True)
    with open(grib_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("GRIB downloaded.")

# --- Dosya boyutu kontrolü ---
if os.path.getsize(grib_file) == 0:
    raise Exception("Downloaded GRIB file is empty!")

# --- xarray ile aç (cfgrib idx hatasına karşı) ---
def open_grib(local_file):
    try:
        ds = xr.open_dataset(
            local_file,
            engine="cfgrib",
            filter_by_keys={'typeOfLevel': 'surface'},
            backend_kwargs={"indexpath": ""}  # <<< EOF hatası için
        )
    except Exception as e1:
        print("Surface level açılmazsa fallback 'atmosphereSingleLayer'...")
        try:
            ds = xr.open_dataset(
                local_file,
                engine="cfgrib",
                filter_by_keys={'typeOfLevel': 'atmosphereSingleLayer'},
                backend_kwargs={"indexpath": ""}  # <<< EOF hatası için
            )
        except Exception as e2:
            raise RuntimeError(f"GRIB açılırken hata: {e1}\n{e2}")
    return ds

ds = open_grib(grib_file)

# --- İskoçya slice ---
lat_slice = slice(55.5, 58)
lon_slice = slice(-3.5, -1)

wind = ds['10m_u_component_of_wind'].sel(latitude=lat_slice, longitude=lon_slice)
solar = ds['surface_downwelling_shortwave_radiation'].sel(latitude=lat_slice, longitude=lon_slice)

windMW = [int(np.mean(wind.isel(time=i).values) * 100) for i in range(5)]
solarMW = [int(np.mean(solar.isel(time=i).values) / 10) for i in range(5)]

forecast = {"days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
            "windMW": windMW,
            "solarMW": solarMW}

os.makedirs("data", exist_ok=True)
with open('data/scotland_forecast.json', 'w') as f:
    json.dump(forecast, f)

# --- Price & Volume örnek ---
ELEXON_KEY = "0fad4fex2qqke42"
price = [50, 48, 46, 52, 49]
volume = [400, 380, 420, 390, 410]

pv = {"days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
      "price": price,
      "volume": volume}

with open('data/price_volume.json', 'w') as f:
    json.dump(pv, f)

print("Forecast and price/volume JSONs created successfully!")
