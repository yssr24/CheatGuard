from django.db import models

class SessionFolder(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class UploadedImage(models.Model):
    folder = models.ForeignKey(SessionFolder, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploaded_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} in folder {self.folder.name}"