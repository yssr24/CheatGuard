from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('playground/', views.playground, name='playground'),
    path('about/', views.about, name='about'),
    path('folder/<int:folder_id>/', views.folder_detail, name='folder_detail'),
    path('delete_folder/<int:folder_id>/', views.delete_folder, name='delete_folder'),
    path('video_feed/<str:device_id>/', views.video_feed, name='video_feed'),
    path('upload_image/<int:folder_id>/', views.upload_image, name='upload_image'),
    path('folder_images/<int:folder_id>/', views.folder_images, name='folder_images'),
]