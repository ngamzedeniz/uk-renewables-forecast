import xarray as xr
import numpy as np

# İskoçya koordinatları
lat_slice = slice(55.5, 58)
lon_slice = slice(-3.5, -1)

def find_variable(ds, candidates):
    """
    Verilen DataSet içinde candidates listesinde bulunan ilk geçerli değişkeni döndürür.
    """
    for name in candidates:
        if name in ds.variables:
            return ds[name]
    return None

def get_wind(ds_surface):
    """
    GRIB'den uygun u10/v10 değişkenlerini bulur ve rüzgar hızını hesaplar.
    """
    u_candidates = ['u10', '10u', '10m_u_component_of_wind', 'UGRD_10m_above_ground']
    v_candidates = ['v10', '10v', '10m_v_component_of_wind', 'VGRD_10m_above_ground']

    u = find_variable(ds_surface, u_candidates)
    v = find_variable(ds_surface, v_candidates)

    if u is None or v is None:
        raise KeyError("GRIB içinde uygun rüzgar bileşenleri bulunamadı!")

    # İskoçya koordinatlarını seç
    u_sel = u.sel(latitude=lat_slice, longitude=lon_slice)
    v_sel = v.sel(latitude=lat_slice, longitude=lon_slice)

    # Rüzgar hızını hesapla
    wind = np.sqrt(u_sel**2 + v_sel**2)
    return wind

def get_solar(ds_surface):
    """
    GRIB'den kısa dalga radyasyonu değişkenini bulur.
    """
    solar_candidates = ['surface_downwelling_shortwave_radiation', 'DSWRF_surface']
    solar = find_variable(ds_surface, solar_candidates)
    if solar is None:
        raise KeyError("GRIB içinde uygun güneş radyasyonu bulunamadı!")
    return solar.sel(latitude=lat_slice, longitude=lon_slice)
