import requests
import json
import xarray as xr
import numpy as np
from datetime import datetime

# -----------------------------
# 1. Güncel GFS GRIB Dosyasını İndir
# -----------------------------
now = datetime.utcnow()
date_str = now.strftime('%Y%m%d')
hour_str = now.strftime('%H')

# Güncel GFS 0.25° dosyası
gfs_url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{date_str}/{hour_str}/atmos/gfs.t{hour_str}z.pgrb2.0p25.f000"

r = requests.get(gfs_url, allow_redirects=True)
with open("gfs_0p25_latest.grib", "wb") as f:
    f.write(r.content)

# -----------------------------
# 2. GFS Verilerini Oku ve İskoçya Bölgesine Filtrele
# -----------------------------
ds = xr.open_dataset("gfs_0p25_latest.grib", engine="cfgrib")
lat_slice = slice(55.5, 58)
lon_slice = slice(-3.5, -1)

wind = ds['10m_u_component_of_wind'].sel(latitude=lat_slice, longitude=lon_slice)
solar = ds['surface_downwelling_shortwave_radiation'].sel(latitude=lat_slice, longitude=lon_slice)

windMW = [int(np.mean(wind.isel(time=i).values)*100) for i in range(5)]
solarMW = [int(np.mean(solar.isel(time=i).values)/10) for i in range(5)]

forecast = {
    "days": ["Day 1","Day 2","Day 3","Day 4","Day 5"],
    "windMW": windMW,
    "solarMW": solarMW
}

with open("data/scotland_forecast.json","w") as f:
    json.dump(forecast, f)

# -----------------------------
# 3. Elexon Price & Volume Verisi
# -----------------------------
ELEXON_KEY = "0fad4fex2qqke42"

# Örnek olarak P114 dosyalarını çekiyoruz
elexon_url = f"https://downloads.elexonportal.co.uk/p114/list?key={ELEXON_KEY}"
r = requests.get(elexon_url)
# Burada gerçek veriyi parse et; şimdilik örnek olarak ilk 5 değeri kullanıyoruz
price = [50,48,46,52,49]  # Gerçek veriyi buraya parse et
volume = [400,380,420,390,410]  # Gerçek veriyi buraya parse et

pv = {
    "days": ["Day 1","Day 2","Day 3","Day 4","Day 5"],
    "price": price,
    "volume": volume
}

with open("data/price_volume.json","w") as f:
    json.dump(pv,f)

print("Forecast and Price/Volume JSON files updated successfully.")
