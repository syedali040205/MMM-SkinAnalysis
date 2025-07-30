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
import pandas as pd
import random as r
# Define FixedDropout
class FixedDropout(Dropout):
    def __init__(self, rate, **kwargs):
        super().__init__(rate, **kwargs)

    def call(self, inputs, training=None):
        if training:
            return super().call(inputs, training=True)
        return inputs
# Load the skincare dataset
data = pd.read_csv("//home/pi//MagicMirror//modules//MMM-SkinAnalysis//recommendations.csv")
random_int = r.randint(0,4)
def get_recommendation(skin_condition):
    # Filter recommendations for the given skin condition
    recommendation = data[data["Skin Condition"].str.lower() == skin_condition.lower()]
    
    if not recommendation.empty:
        ingredients = recommendation["Recommended Ingredients"].values[0]
        products = recommendation["Product Suggestions"].values[0]
        tips = recommendation["Skincare Tips"].values[0]
        return f"{skin_condition} <br> -Use : {ingredients} <br> - Products: {products} <br> - Tips: {tips} <br>"
    else:
        return "No Face Detected"

# Example usage
# Replace this with actual AI detection
# Register FixedDropout and swish in custom_objects
custom_objects = {
    'FixedDropout': FixedDropout,
    'swish': swish
}

# Load the model
model = load_model("/home/pi/MagicMirror/modules/MMM-SkinAnalysis/skin.h5", custom_objects=custom_objects, compile=False)

# Load class indices
with open(os.path.abspath("/home/pi/MagicMirror/modules/MMM-SkinAnalysis/class_indices.pkl"), "rb") as f:
    class_indices = pickle.load(f)

# Reverse the class indices for label mapping
reverse_class_indices = {v: k for k, v in class_indices.items()}

# Define image size
image_size = (224, 224)

# Shared variable to hold the latest prediction
latest_prediction = "Initializing..."
no_face_counter = 0  # Track consecutive frames with no face

# Function to predict label asynchronously
def predict_label_async(frame_queue):
    global latest_prediction
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()  # Get the latest frame
            face_image = cv2.resize(frame, image_size)
            face_image = np.expand_dims(face_image, axis=0) / 255.0
            predictions = model.predict(face_image, verbose=0)  # Use the imported model
            latest_prediction = reverse_class_indices[np.argmax(predictions)]
            recommendation = get_recommendation(latest_prediction)
            print(recommendation)
            time.sleep(7)
            sys.stdout.flush()  # Ensure the output is sent immediately


cap = cv2.VideoCapture("//dev//video2")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# Verify if the camera opened successfully
if not cap.isOpened():
    print("❌ Error: Unable to access /dev/video2. Check camera connection.")
    sys.exit(1)

# Queue to hold frames for predictions
frame_queue = Queue(maxsize=50)  # Keep only the most recent frame for predictions

# Start the asynchronous prediction thread
prediction_thread = threading.Thread(target=predict_label_async, args=(frame_queue,), daemon=True)
prediction_thread.start()

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Main loop to display frames
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Error: Failed to read frame from /dev/video0")
        break

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        time.sleep(5)
        latest_prediction = "No Face Detected"
        print("Analyzing....")  # Update label if no faces are detected
        sys.stdout.flush()

        no_face_counter += 1  # Increment counter

        if no_face_counter >= 2000:  # If no face detected for ~2 seconds
            print("No face detected for too long. Stopping Skin Analysis...")
            break  # Exit the loop and stop Skin Analysis

    else:
        no_face_counter = 0  # Reset counter if a face is detected

        # Add the current frame to the queue (if not full)
        if not frame_queue.full():
            frame_queue.put(frame)

    # Introduce a small delay to reduce CPU usage
    time.sleep(0.01)

    # Break loop on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
