from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .models import Detection
import cv2
import numpy as np
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="D6NnigvMvhlT8B4yVYU4"
)
model_id = "offline-exam-monitoring-3-rub5m-y5zbj/1"

def dashboard(request):
    return render(request, 'monitoring/dashboard.html')

def analytics(request):
    detections = Detection.objects.all()
    return render(request, 'monitoring/analytics.html', {'detections': detections})

def visualize(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)

        # Run inference
        image_path = fs.path(filename)
        result = CLIENT.infer(image_path, model_id=model_id)
        detections = result['predictions']

        # Save detection to database
        detection = Detection(image=image, detections=detections)
        detection.save()

        # Load the image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Draw bounding boxes and labels
        for detection in detections:
            x, y, width, height = detection['x'], detection['y'], detection['width'], detection['height']
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{detection['class']} ({detection['confidence']:.2f})"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Save the annotated image
        annotated_image_path = fs.path('annotated_' + filename)
        cv2.imwrite(annotated_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        return render(request, 'monitoring/visualize.html', {
            'uploaded_file_url': uploaded_file_url,
            'annotated_image_url': fs.url('annotated_' + filename)
        })

    return render(request, 'monitoring/visualize.html')