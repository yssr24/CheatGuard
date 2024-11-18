from django.db import models

class Detection(models.Model):
    image = models.ImageField(upload_to='images/')
    timestamp = models.DateTimeField(auto_now_add=True)
    detections = models.JSONField()

    def __str__(self):
        return f"Detection {self.id} at {self.timestamp}"