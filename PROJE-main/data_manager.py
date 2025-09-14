# data_manager.py
import csv

class DataManager:
    def __init__(self):
        self.plant_data = self.load_plant_data('plant_data.csv')
        self.soil_data = self.load_soil_data('soil_data.csv')

    def load_plant_data(self, filename):
        """CSV dosyasından bitki verilerini yükler."""
        plant_data = {}
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    plant_name = row['plant_name']
                    stage = row['stage']
                    # Buradaki değişikliği yaptık: int() yerine float() kullanıldı
                    duration = float(row['duration_days'])
                    kc = float(row['kc_value'])

                    if plant_name not in plant_data:
                        plant_data[plant_name] = {"growth_stages": {}}
                    
                    plant_data[plant_name]["growth_stages"][stage] = {
                        "duration": duration,
                        "kc": kc
                    }
        except FileNotFoundError:
            print(f"Hata: '{filename}' dosyası bulunamadı.")
            return {}
        except Exception as e:
            print(f"Hata: '{filename}' okunurken bir sorun oluştu: {e}")
            return {}
        return plant_data

    def load_soil_data(self, filename):
        """CSV dosyasından toprak verilerini yükler."""
        soil_data = {}
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    soil_data[row['soil_name']] = {'awc': float(row['awc_mm_per_m'])}
        except FileNotFoundError:
            print(f"Hata: '{filename}' dosyası bulunamadı.")
            return {}
        except Exception as e:
            print(f"Hata: '{filename}' okunurken bir sorun oluştu: {e}")
            return {}
        return soil_data

    def get_kc(self, plant_type, day_of_growth):
        """Bitkinin büyüme evresine göre Kc değerini döndürür."""
        plant_stages = self.plant_data.get(plant_type, None)
        if not plant_stages:
            return None

        total_days = 0
        for stage_name, stage_info in plant_stages["growth_stages"].items():
            total_days += stage_info["duration"]
            if day_of_growth <= total_days:
                return stage_info["kc"]
        
        return None
    
    def get_awc(self, soil_type):
        """Toprağın kullanılabilir su kapasitesini (AWC) döndürür."""
        return self.soil_data.get(soil_type, None)
