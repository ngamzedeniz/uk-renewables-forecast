# generate_forecast.py

from datetime import datetime
import xarray as xr

def get_gfs_latest_url():
    """
    Güncel GFS 0.25° yüzey verisinin URL'sini oluşturur.
    """
    now = datetime.utcnow()
    YYYYMMDD = now.strftime("%Y%m%d")
    HH = str((now.hour // 6) * 6).zfill(2)  # En yakın 00, 06, 12, 18 saatleri
    # Forecast hour 000 (şu anki analiz)
    forecast_hour = "000"

    url = (
        f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
        f"gfs.{YYYYMMDD}/{HH}/atmos/gfs.t{HH}z.pgrb2.0p25.f{forecast_hour}"
    )
    return url

def main():
    grib_file = get_gfs_latest_url()
    print(f"Using GFS file: {grib_file}")

    try:
        # Surface seviyesindeki veriyi aç
        ds = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'surface'})
    except Exception as e:
        print(f"Error opening GRIB with surface level: {e}")
        # Eğer surface yoksa, atmosfer tek katman verisini dene
        ds = xr.open_dataset(grib_file, engine='cfgrib', filter_by_keys={'typeOfLevel': 'atmosphereSingleLayer'})

    print(ds)

if __name__ == "__main__":
    main()
