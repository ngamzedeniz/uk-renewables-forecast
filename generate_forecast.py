import requests, json
import pandas as pd
import numpy as np
import xarray as xr

# --- 1. GFS GRIB dosyasını indir ---
GFS_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.0p25/latest/gfs.t00z.pgrb2.0p25.f000"
grib_file = "gfs_0p25_latest.grib"

print("Downloading latest GFS GRIB...")
r = requests.get(GFS_URL)
with open(grib_file, "wb") as f:
    f.write(r.content)
print("GRIB downloaded.")

# --- 2. GFS verilerini oku (Iskocya için) ---
ds = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'surface'})

lat_slice = slice(55.5, 58)
lon_slice = slice(-3.5, -1)

wind = ds['10m_u_component_of_wind'].sel(latitude=lat_slice, longitude=lon_slice)
solar = ds['surface_downwelling_shortwave_radiation'].sel(latitude=lat_slice, longitude=lon_slice)

windMW = [int(np.mean(wind.isel(time=i).values)*100) for i in range(5)]
solarMW = [int(np.mean(solar.isel(time=i).values)/10) for i in range(5)]

forecast = {
    "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
    "windMW": windMW,
    "solarMW": solarMW
}

with open('data/scotland_forecast.json','w') as f:
    json.dump(forecast,f)

# --- 3. Elexon Price & Volume verisi ---
ELEXON_KEY = "0fad4fex2qqke42"
url = f"https://downloads.elexonportal.co.uk/p114/list?key={ELEXON_KEY}"
try:
    r = requests.get(url).json()
except:
    r = {}  # Eğer API çalışmazsa boş dict
# Örnek veri
price = [50,48,46,52,49]
volume = [400,380,420,390,410]

pv = {"days":["Day 1","Day 2","Day 3","Day 4","Day 5"],"price":price,"volume":volume}
with open('data/price_volume.json','w') as f:
    json.dump(pv,f)

print("Forecast and Price/Volume JSONs created successfully.")
