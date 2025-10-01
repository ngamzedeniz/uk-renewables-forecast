import xarray as xr
import numpy as np
import pandas as pd
import sys

# İskoçya koordinatları
lat_slice = slice(55.5, 58)
lon_slice = slice(-3.5, -1)

def find_variable(ds, candidates):
    for name in candidates:
        if name in ds.variables:
            return ds[name]
    return None

def get_wind(ds_surface):
    u_candidates = ['u10', '10u', '10m_u_component_of_wind', 'UGRD_10m_above_ground']
    v_candidates = ['v10', '10v', '10m_v_component_of_wind', 'VGRD_10m_above_ground']

    u = find_variable(ds_surface, u_candidates)
    v = find_variable(ds_surface, v_candidates)
    if u is None or v is None:
        raise KeyError("GRIB içinde uygun rüzgar bileşenleri bulunamadı!")

    u_sel = u.sel(latitude=lat_slice, longitude=lon_slice)
    v_sel = v.sel(latitude=lat_slice, longitude=lon_slice)
    wind = np.sqrt(u_sel**2 + v_sel**2)
    return wind

def get_solar(ds_surface):
    solar_candidates = ['surface_downwelling_shortwave_radiation', 'DSWRF_surface']
    solar = find_variable(ds_surface, solar_candidates)
    if solar is None:
        raise KeyError("GRIB içinde uygun güneş radyasyonu bulunamadı!")
    return solar.sel(latitude=lat_slice, longitude=lon_slice)

if __name__ == "__main__":
    grib_file = sys.argv[1] if len(sys.argv) > 1 else "data/gfs_latest.grib"

    ds = xr.open_dataset(grib_file, engine="cfgrib")

    wind = get_wind(ds)
    solar = get_solar(ds)

    wind_mean = wind.mean(dim=["latitude", "longitude"]).to_pandas()
    solar_mean = solar.mean(dim=["latitude", "longitude"]).to_pandas()

    df = pd.DataFrame({
        "time": wind_mean.index,
        "wind_speed": wind_mean.values,
        "solar_radiation": solar_mean.values
    })

    df.to_csv("forecast_output.csv", index=False)
    print("✅ forecast_output.csv kaydedildi!")
