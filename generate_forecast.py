import os
import requests
import xarray as xr
import numpy as np
import json

# --- GRIB URL (0.25° latest, İskoçya) ---
GFS_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.0p25/latest/gfs.t00z.pgrb2.0p25.f000"
LOCAL_GRIB = "gfs_latest.grib"

# --- Dosyayı indir ---
def download_grib(url, local_file):
    if os.path.exists(local_file) and os.path.getsize(local_file) > 50000000:  # 50 MB kontrolü
        print(f"{local_file} zaten var, tekrar indirmeye gerek yok.")
        return

    print(f"Downloading GFS GRIB from {url} ...")
    r = requests.get(url, stream=True)
    with open(local_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Download complete. File size: {os.path.getsize(local_file)} bytes")

# --- GFS dosyasını aç ---
def open_grib(local_file):
    try:
        ds = xr.open_dataset(local_file, engine="cfgrib",
                             filter_by_keys={"typeOfLevel": "surface"},
                             backend_kwargs={"indexpath": ""})
        print("Surface level data loaded.")
        return ds
    except Exception as e1:
        print("Surface level açılmadı, atmosphereSingleLayer ile deniyor...")
        try:
            ds = xr.open_dataset(local_file, engine="cfgrib",
                                 filter_by_keys={"typeOfLevel": "atmosphereSingleLayer"},
                                 backend_kwargs={"indexpath": ""})
            print("Atmosphere single layer data loaded.")
            return ds
        except Exception as e2:
            raise RuntimeError(f"GRIB açılırken hata: {e1}\n{e2}")

# --- İskoçya slice ve MW hesaplama ---
def extract_scotland_forecast(ds):
    lat_slice = slice(55.5, 58)
    lon_slice = slice(-3.5, -1)

    try:
        wind = ds['10m_u_component_of_wind'].sel(latitude=lat_slice, longitude=lon_slice)
    except KeyError:
        wind = ds['10m_v_component_of_wind'].sel(latitude=lat_slice, longitude=lon_slice)

    try:
        solar = ds['surface_downwelling_shortwave_radiation'].sel(latitude=lat_slice, longitude=lon_slice)
    except KeyError:
        solar = np.zeros_like(wind)

    windMW = [int(np.mean(wind.isel(time=i).values) * 100) for i in range(min(5, len(wind.time)))]
    solarMW = [int(np.mean(solar.isel(time=i).values) / 10) for i in range(min(5, len(solar.time)))]

    forecast = {
        "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "windMW": windMW,
        "solarMW": solarMW
    }

    os.makedirs("data", exist_ok=True)
    with open('data/scotland_forecast.json', 'w') as f:
        json.dump(forecast, f)
    print("Forecast JSON created successfully!")

# --- Main ---
def main():
    download_grib(GFS_URL, LOCAL_GRIB)
    ds = open_grib(LOCAL_GRIB)
    extract_scotland_forecast(ds)

if __name__ == "__main__":
    main()
