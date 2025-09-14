# weather.py
import requests

class WeatherAPIClient:
    def __init__(self, api_key=None):
        # Open-Meteo.com API anahtarı gerektirmez
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.api_key = api_key # İleride ücretli API'lar için kullanılabilir

    def get_forecast(self, latitude, longitude, days=7):
        """
        Belirtilen enlem ve boylam için hava durumu tahminlerini çeker.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "et0_fao_evapotranspiration,precipitation_sum",
            "forecast_days": days,
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Hata durumunda istisna fırlatır
            data = response.json()
            
            # API'dan gelen veriyi daha kullanışlı bir formata dönüştür
            forecast_list = []
            if 'daily' in data:
                dates = data['daily']['time']
                et0_values = data['daily']['et0_fao_evapotranspiration']
                precip_values = data['daily']['precipitation_sum']
                
                for i in range(len(dates)):
                    forecast_list.append({
                        'date': dates[i],
                        'et0': et0_values[i],
                        'precipitation': precip_values[i]
                    })
            
            return forecast_list
        except requests.exceptions.RequestException as e:
            raise Exception(f"API isteği başarısız oldu: {e}")