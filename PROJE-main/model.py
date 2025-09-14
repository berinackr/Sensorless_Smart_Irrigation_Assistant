# model.py
from datetime import date
from data_manager import DataManager

class SoilWaterBalanceModel:
    def __init__(self, data_manager, planting_date, plant_type, soil_type, is_potted, cultivation_area_m2, pot_volume_liters):
        self.data_manager = data_manager
        self.planting_date = planting_date
        self.plant_type = plant_type
        self.soil_type = soil_type
        self.is_potted = is_potted
        self.cultivation_area_m2 = cultivation_area_m2
        self.pot_volume_liters = pot_volume_liters
        self.current_water_deficit = 0 # Başlangıçta su açığı yok varsayımı (tarla kapasitesi)
        
        # Kullanılabilir su kapasitesini (AWC) al
        awc_data = self.data_manager.get_awc(self.soil_type)
        if awc_data and 'awc' in awc_data:
            self.awc_mm_per_m = awc_data['awc']
        else:
            self.awc_mm_per_m = 0 # Güvenlik için varsayılan değer
        
        # Saksı bitkileri için toplam AWC'yi yaklaşık saksı derinliğine göre ayarla (örn: 20 cm)
        if self.is_potted:
            # 20 cm'lik saksı derinliği varsayımı
            pot_depth_m = 0.2
            self.max_awc_mm = self.awc_mm_per_m * pot_depth_m
        else:
            self.max_awc_mm = self.awc_mm_per_m # Tarla bitkileri için 1m kök derinliği varsayımı

    def update_and_recommend(self, forecast_date_str, et0, rainfall):
        """
        Günlük su dengesini günceller ve sulama önerisi yapar.
        """
        # Burada forecast_date_str'yi datetime.date objesine dönüştür
        forecast_date = date.fromisoformat(forecast_date_str)
        
        days_since_planting = (forecast_date - self.planting_date).days
        kc = self.data_manager.get_kc(self.plant_type, days_since_planting)
        
        if kc is None:
            return {"amount": 0, "liters": 0, "message": "Bitkinin büyüme evresi tamamlanmış."}

        # ETc hesaplaması
        etc = kc * et0

        # Günlük su dengesini güncelle
        self.current_water_deficit += etc
        self.current_water_deficit -= rainfall # Yağışı çıkar
        
        # Su açığını negatif olmaktan koru
        if self.current_water_deficit < 0:
            self.current_water_deficit = 0
            
        # Sulama ihtiyacını belirle
        irrigation_amount_mm = 0
        message = "Su ihtiyacı yok."
        
        # Örnek sulama eşiği: AWC'nin %50'si
        irrigation_threshold = self.max_awc_mm * 0.5 
        
        if self.current_water_deficit >= irrigation_threshold:
            irrigation_amount_mm = self.current_water_deficit
            message = "Sulama önerilir."
            self.current_water_deficit = 0 # Sulama sonrası su açığını sıfırla

        # mm cinsinden sulama miktarını litreye çevir
        if self.is_potted:
            # Sulama miktarını pot hacmine oranla hesapla
            total_water_capacity_liters = self.pot_volume_liters * 0.5  # Basit bir varsayım
            liters = (irrigation_amount_mm / self.max_awc_mm) * total_water_capacity_liters
        else:
            liters = irrigation_amount_mm * self.cultivation_area_m2
        
        return {"amount": irrigation_amount_mm, "liters": liters, "message": message}
    
    def calibrate_with_feedback(self, feedback):
        """
        Kullanıcı geri bildirimini kullanarak modeli adapte eden ML çekirdeği.
        NOT: Bu fonksiyon sadece bir yer tutucudur. Gerçek ML modeli buraya entegre edilmelidir.
        """
        print(f"Kullanıcı geri bildirimi alınıyor: '{feedback}'.")
        # Burada bir ML algoritması (örn: Bulanık Mantık veya Bayesçi model) 
        # `self.current_water_deficit` gibi dahili parametreleri düzeltir.
        if feedback == "kuru":
            print("Model tahminleri revize ediliyor. Bir sonraki sulama tavsiyesi artırılabilir.")
            # self.current_water_deficit += a_small_value
        elif feedback == "ıslak":
            print("Model tahminleri revize ediliyor. Bir sonraki sulama tavsiyesi azaltılabilir.")
            # self.current_water_deficit -= a_small_value
        else:
            print("Geri bildirim modelin tahminini onaylıyor.")
