from django.core.management.base import BaseCommand
from catalog.models import Phone

class Command(BaseCommand):
    help = "Seed phone data"

    def handle(self, *args, **kwargs):
        data = [
            {"brand":"Samsung","model":"Galaxy A34","price_inr":19999,"camera_mp":48,"ois":False,"eis":True,"battery_mah":5000,"fast_charge_w":25,"screen_size_in":6.6,"compact":False,"ram_gb":6,"storage_gb":128},
            {"brand":"Google","model":"Pixel 8a","price_inr":31999,"camera_mp":64,"ois":True,"eis":True,"battery_mah":4500,"fast_charge_w":18,"screen_size_in":6.1,"compact":True,"ram_gb":8,"storage_gb":128},
            {"brand":"OnePlus","model":"12R","price_inr":27999,"camera_mp":50,"ois":True,"eis":True,"battery_mah":5000,"fast_charge_w":80,"screen_size_in":6.7,"compact":False,"ram_gb":8,"storage_gb":256},
            {"brand":"Xiaomi","model":"Redmi Note 12","price_inr":12999,"camera_mp":108,"ois":False,"eis":True,"battery_mah":5000,"fast_charge_w":33,"screen_size_in":6.67,"compact":False,"ram_gb":6,"storage_gb":128},
            {"brand":"Realme","model":"Narzo 70","price_inr":14999,"camera_mp":50,"ois":False,"eis":True,"battery_mah":6000,"fast_charge_w":45,"screen_size_in":6.5,"compact":False,"ram_gb":6,"storage_gb":128},
            {"brand":"Samsung","model":"Galaxy S23 FE","price_inr":41999,"camera_mp":50,"ois":True,"eis":True,"battery_mah":3900,"fast_charge_w":25,"screen_size_in":6.1,"compact":True,"ram_gb":8,"storage_gb":128},
            {"brand":"Vivo","model":"Y100","price_inr":15999,"camera_mp":64,"ois":False,"eis":True,"battery_mah":5000,"fast_charge_w":44,"screen_size_in":6.38,"compact":False,"ram_gb":8,"storage_gb":128},
            {"brand":"Poco","model":"X5 Pro","price_inr":21999,"camera_mp":108,"ois":False,"eis":True,"battery_mah":5000,"fast_charge_w":67,"screen_size_in":6.67,"compact":False,"ram_gb":8,"storage_gb":256},
            {"brand":"Oppo","model":"A78","price_inr":12999,"camera_mp":50,"ois":False,"eis":True,"battery_mah":5000,"fast_charge_w":33,"screen_size_in":6.56,"compact":False,"ram_gb":6,"storage_gb":128},
            {"brand":"Itel","model":"A48","price_inr":7999,"camera_mp":8,"ois":False,"eis":False,"battery_mah":4000,"fast_charge_w":10,"screen_size_in":6.1,"compact":True,"ram_gb":2,"storage_gb":32},
        ]
        Phone.objects.all().delete()
        for d in data:
            Phone.objects.create(**d)
        self.stdout.write(self.style.SUCCESS("Seeded phones"))
