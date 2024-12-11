from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from .models import SessionFolder, UploadedImage
from .forms import SessionFolderForm, UploadedImageForm
from ultralytics import YOLO
import cv2

def dashboard(request):
    session_folders = SessionFolder.objects.all()
    return render(request, 'dashboard.html', {'session_folders': session_folders})

def playground(request):
    if request.method == 'POST' and 'name' in request.POST:
        form = SessionFolderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('playground')
    else:
        form = SessionFolderForm()

    session_folders = SessionFolder.objects.all()
    return render(request, 'playground.html', {'form': form, 'session_folders': session_folders})

def folder_detail(request, folder_id):
    folder = get_object_or_404(SessionFolder, id=folder_id)
    return render(request, 'folder_detail.html', {'folder': folder})

def folder_images(request, folder_id):
    folder = get_object_or_404(SessionFolder, id=folder_id)
    images = UploadedImage.objects.filter(folder=folder)
    image_data = [{'url': image.image.url} for image in images]
    return JsonResponse({'images': image_data})

def delete_folder(request, folder_id):
    if request.method == 'POST':
        folder = get_object_or_404(SessionFolder, id=folder_id)
        folder.delete()
    return redirect('playground')

def about(request):
    return render(request, 'about.html')

model = YOLO('../offline_exam_monitoring_model.pt')

# Map device IDs to integer indices
device_id_map = {}

def index(request):
    return render(request, 'detection/index.html')

def gen(device_id):
    if device_id not in device_id_map:
        device_id_map[device_id] = len(device_id_map)
    camera_index = device_id_map[device_id]
    camera = cv2.VideoCapture(camera_index)
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        results = model(frame)
        annotated_frame = results[0].plot()
        ret, jpeg = cv2.imencode('.jpg', annotated_frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request, device_id):
    return StreamingHttpResponse(gen(device_id),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def upload_image(request, folder_id):
    if request.method == 'POST':
        form = UploadedImageForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save(commit=False)
            uploaded_image.folder = get_object_or_404(SessionFolder, id=folder_id)
            uploaded_image.save()

            # Process the image with YOLO model
            image_path = uploaded_image.image.path
            image = cv2.imread(image_path)
            results = model(image)
            annotated_frame = results[0].plot()

            # Save the annotated image
            annotated_image_path = image_path.replace('.jpg', '_annotated.jpg')
            cv2.imwrite(annotated_image_path, annotated_frame)

            # Count detections
            cheating = sum(1 for result in results[0].boxes if result.cls == 0)  # Assuming class 0 is cheating
            non_cheating = sum(1 for result in results[0].boxes if result.cls == 2)  # Assuming class 2 is non-cheating
            phone = sum(1 for result in results[0].boxes if result.cls == 3)  # Assuming class 3 is phone
            cheating_paper = sum(1 for result in results[0].boxes if result.cls == 1)  # Assuming class 1 is cheating-paper

            response_data = {
                'image_url': uploaded_image.image.url,
                'cheating': cheating,
                'non_cheating': non_cheating,
                'phone': phone,
                'cheating_paper': cheating_paper,
            }
            return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)