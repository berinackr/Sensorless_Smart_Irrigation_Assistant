# main.py
from datetime import date
from weather import WeatherAPIClient
from data_manager import DataManager
from model import SoilWaterBalanceModel

def main():
    """
    Ana fonksiyon: Kullanıcı girdilerini alır,
    API'den verileri çeker ve sulama önerileri sunar.
    """
    print("🌿 Yapay Zeka Destekli Sulama Asistanı")
    print("---------------------------------------")

    # Kullanıcı girdileri
    plant_type = input("Bitki türünü girin (örn: Domates, Biber): ")
    planting_date_str = input("Ekim tarihini girin (YYYY-MM-DD): ")
    planting_date = date.fromisoformat(planting_date_str)
    
    # Kullanıcının yetiştirme ortamını belirlemesi
    is_potted = input("Yetiştirme alanı saksı mı? (evet/hayır): ").lower() == 'evet'
    if is_potted:
        soil_type = input("Toprak tipini girin (örn: Saksı Toprağı): ")
        pot_volume_liters = float(input("Saksı hacmini girin (litre): "))
        cultivation_area_m2 = None
    else:
        cultivation_area_m2 = float(input("Yetiştirme alanını girin (metrekare): "))
        soil_type = input("Toprak tipini girin (örn: Tın, Kumlu Tın, Kil): ")
        pot_volume_liters = None

    # Veri yönetimini başlat
    data_manager = DataManager()
    
    # Hava durumu API istemcisini başlat
    # NOT: Kendi API anahtarınızı buraya girmeniz gerekecek
    weather_api = WeatherAPIClient(api_key="YOUR_API_KEY") 

    # Gelecek 7 gün için tahminleri çek
    # Enlem ve boylamı kullanıcıdan almanız veya varsayılan bir değer kullanmanız gerekebilir
    latitude, longitude = 41.0082, 28.9784  # Örn: İstanbul
    try:
        weather_forecast = weather_api.get_forecast(latitude, longitude, days=7)
    except Exception as e:
        print(f"Hava durumu verileri çekilirken bir hata oluştu: {e}")
        return

    # Ana sulama modelini başlat
    model = SoilWaterBalanceModel(data_manager, planting_date, plant_type, 
                                  soil_type, is_potted, cultivation_area_m2, pot_volume_liters)

    # Günlük sulama önerilerini hesapla ve yazdır
    print("\n💧 Önümüzdeki Günler İçin Sulama Programı:")
    print("---------------------------------------")
    
    for day_data in weather_forecast:
        forecast_date = day_data['date']
        et0 = day_data['et0'] # mm
        rainfall = day_data['precipitation'] # mm

        # Günlük su dengesini güncelle ve sulama önerisi al
        recommendation = model.update_and_recommend(forecast_date, et0, rainfall)
        
        print(f"Tarih: {forecast_date}")
        print(f"   Tahmini ET₀: {et0:.2f} mm, Yağış: {rainfall:.2f} mm")
        print(f"   Öneri: {recommendation['amount']:.2f} mm ({recommendation['liters']:.2f} litre) su verin.")
        print(f"   Not: {recommendation['message']}")

    # Sensörsüz Kalibrasyon için kullanıcı geri bildirimi
    print("\n🌱 Model Hassasiyetini Artırma: Sensörsüz Kalibrasyon")
    print("---------------------------------------")
    feedback = input("Bugün toprağınızın durumu nasıldı? (kuru/orta/ıslak): ")
    model.calibrate_with_feedback(feedback)

if __name__ == "__main__":
    main()
