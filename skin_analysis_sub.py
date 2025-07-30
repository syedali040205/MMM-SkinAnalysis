import cv2
import numpy as np
import threading
from queue import Queue
import time
import sys
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dropout
from tensorflow.keras.activations import swish
import os
import subprocess

# Define FixedDropout
class FixedDropout(Dropout):
    def __init__(self, rate, **kwargs):
        super().__init__(rate, **kwargs)

    def call(self, inputs, training=None):
        if training:
            return super().call(inputs, training=True)
        return inputs

# Register custom objects
custom_objects = {
    'FixedDropout': FixedDropout,
    'swish': swish
}
current_process = None

# Load the model
model = load_model("/home/pi/MagicMirror/modules/MMM-SkinAnalysis/skin.h5", custom_objects=custom_objects, compile=False)

# Load class indices
with open(os.path.abspath("/home/pi/MagicMirror/modules/MMM-SkinAnalysis/class_indices.pkl"), "rb") as f:
    class_indices = pickle.load(f)

# Reverse class indices
reverse_class_indices = {v: k for k, v in class_indices.items()}

# Define image size
image_size = (224, 224)

# Shared variable for prediction
latest_prediction = "Initializing..."
no_face_counter = 0
cap = None  # Ensure cap is globally defined

# Function to clear camera cache before analysis
def clear_camera_cache():
    global cap
    if cap is not None:
        print(" Releasing camera resources before starting analysis...")
        cap.release()
        cv2.destroyAllWindows()
        time.sleep(4)  # Allow camera to reset

    print(" Reinitializing camera...")
    cap = cv2.VideoCapture(0)  # Open camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

# Function to predict label asynchronously
def predict_label_async(frame_queue):
    global latest_prediction
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            face_image = cv2.resize(frame, image_size)
            face_image = np.expand_dims(face_image, axis=0) / 255.0
            predictions = model.predict(face_image, verbose=0)
            latest_prediction = reverse_class_indices[np.argmax(predictions)]
            print(f"️ Skin Analysis Prediction: {latest_prediction}")
            sys.stdout.flush()

# Ensure camera is cleared before starting
clear_camera_cache()

# Queue for frames
frame_queue = Queue(maxsize=50)

# Start prediction thread
prediction_thread = threading.Thread(target=predict_label_async, args=(frame_queue,), daemon=True)
prediction_thread.start()

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Main loop
while True:
    if cap is None or not cap.isOpened():
        print("️ Camera not opened. Reinitializing...")
        clear_camera_cache()

    ret, frame = cap.read()
    if not ret:
        print("Camera read failed. Retrying...")
        clear_camera_cache()
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        latest_prediction = "No Face Detected"
        print("No Face Detected")
        sys.stdout.flush()

        no_face_counter += 1
        if no_face_counter >= 200:  # If no face detected for 2 seconds
            print("No face detected for too long. Stopping Skin Analysis...")
            break

    else:
        no_face_counter = 0
        if not frame_queue.full():
            frame_queue.put(frame)

    time.sleep(0.01)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release camera when done
if cap is not None:
    cap.release()
cv2.destroyAllWindows()