import cfgrib
import xarray as xr
import json
import numpy as np

# GFS 0.25° grib dosyasını aç
ds = xr.open_dataset('gfs_0p25_20250930_00.grib', engine='cfgrib')

# İskoçya koordinatları
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

with open('data/scotland_forecast.json','w') as f:
    json.dump(forecast, f)
