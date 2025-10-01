import xarray as xr
import requests
import os
from datetime import datetime

def download_grib():
    # Bugünün tarihini YYYYMMDD formatında al
    today = datetime.utcnow().strftime('%Y%m%d')
    cycle = '18'  # UTC cycle (00, 06, 12, 18)
    forecast_hour = 'f000'

    # NOAA mirror URL
    url = f"https://tgftp.nws.noaa.gov/data/nccf/com/gfs/prod/gfs.{today}/{cycle}/atmos/gfs.t{cycle}z.pgrb2.0p25.{forecast_hour}"
    local_file = "gfs_latest.grib"

    # Eğer dosya yoksa veya boşsa indir
    if not os.path.exists(local_file) or os.path.getsize(local_file) == 0:
        print(f"Downloading GFS file: {url}")
        headers = {"User-Agent": "Mozilla/5.0"}  # Bazı sunucular User-Agent ister
        r = requests.get(url, headers=headers, stream=True)
        if r.status_code == 200:
            with open(local_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download complete.")
        else:
            raise Exception(f"Failed to download GRIB file, status code: {r.status_code}")
    else:
        print("GRIB file already exists.")

    return local_file

def main():
    grib_file = download_grib()

    # Surface level verilerini açmayı dene
    try:
        ds_surface = xr.open_dataset(grib_file, engine='cfgrib',
                                     filter_by_keys={'typeOfLevel': 'surface'})
        print("Surface level data loaded successfully.")
    except Exception as e1:
        print(f"Surface level açılmazsa fallback 'atmosphereSingleLayer'...\nError: {e1}")
        try:
            ds_surface = xr.open_dataset(grib_file, engine='cfgrib',
                                         filter_by_keys={'typeOfLevel': 'atmosphereSingleLayer'})
            print("Atmosphere single layer data loaded successfully as fallback.")
        except Exception as e2:
            raise RuntimeError(f"GRIB açılırken hata:\nSurface: {e1}\nAtmosphereSingleLayer: {e2}")

if __name__ == "__main__":
    main()
