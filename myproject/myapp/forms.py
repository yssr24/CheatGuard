from django import forms
from .models import SessionFolder, UploadedImage

class SessionFolderForm(forms.ModelForm):
    class Meta:
        model = SessionFolder
        fields = ['name']

class UploadedImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']