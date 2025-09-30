import requests, json

SCRIPTING_KEY = "0fad4fex2qqke42"

# Elexon URLs (örnek)
price_url = f"https://downloads.elexonportal.co.uk/file/download/BESTVIEWPRICES_FILE?key={SCRIPTING_KEY}"
volume_url = f"https://downloads.elexonportal.co.uk/file/download/TLM_FILE?key={SCRIPTING_KEY}"

# Dummy veri (workflow çalışınca gerçek veri çekilecek)
forecast = {
    "days": ["Day1","Day2","Day3","Day4","Day5"],
    "price": [50,48,46,52,49],
    "volume": [400,380,420,390,410]
}
with open("price_volume.json","w") as f:
    json.dump(forecast,f)

gfs_forecast = {
    "days": ["Day1","Day2","Day3","Day4","Day5"],
    "windMW": [100,120,90,110,105],
    "solarMW": [80,75,85,90,95]
}
with open("scotland_forecast.json","w") as f:
    json.dump(gfs_forecast,f)

print("Forecast JSONs updated!")
