from django.db import models

class Phone(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    price_inr = models.IntegerField()  # integer rupees
    camera_mp = models.IntegerField(null=True, blank=True)
    ois = models.BooleanField(default=False)
    eis = models.BooleanField(default=False)
    battery_mah = models.IntegerField(null=True, blank=True)
    fast_charge_w = models.IntegerField(null=True, blank=True)
    screen_size_in = models.FloatField(null=True, blank=True)
    weight_g = models.IntegerField(null=True, blank=True)
    compact = models.BooleanField(default=False)  # custom flag for compactness
    os = models.CharField(max_length=50, default="Android")
    ram_gb = models.IntegerField(null=True, blank=True)
    storage_gb = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("brand", "model")

    def __str__(self):
        return f"{self.brand} {self.model}"
