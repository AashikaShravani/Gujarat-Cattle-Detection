from flask import Flask, render_template, Response, send_file, jsonify
import numpy as np
import cv2
import argparse
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

# Argument parsing
ap = argparse.ArgumentParser(description='Script to run MobileNet-SSD object detection network')
ap.add_argument('-v', '--video', type=str, default=r'C:\Users\Aathresh\PycharmProjects\Gujarat Hackathon\2.mp4',
                help='Path to video file. If empty, webcam stream will be used')
ap.add_argument('-p', '--prototxt', required=True,
                help="Path to Caffe 'deploy' prototxt file")
ap.add_argument('-m', '--model', required=True,
                help='Path to weights for Caffe model')
ap.add_argument('-l', '--labels', required=True,
                help='Path to labels for the dataset')
ap.add_argument('-c', '--confidence', type=float, default=0.2,
                help='Minimum probability to filter weak detections')
args = vars(ap.parse_args())

# Initialize class labels of the dataset
CLASSES = [line.strip() for line in open(args['labels'])]
print('[INFO]', CLASSES)

# Generate random bounding box colors for each class label
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# Load Caffe model from disk
print("[INFO] Loading model")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# Open video capture from a file or capture device
print("[INFO] Starting video stream")
if args['video']:
    cap = cv2.VideoCapture(args['video'])
else:
    cap = cv2.VideoCapture(0)

# Open a text file for writing
output_file = open('output.txt', 'w')

# Initialize variables for the chart data
chart_labels = []
chart_accuracy = []

@app.route('/')
def index():
    return render_template('index.html')

# Generator function to capture video frames and update chart data
def generate():
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        (h, w) = frame.shape[:2]

        # MobileNet requires fixed dimensions for the input image(s)
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        # Pass the blob through the network and obtain the detections and predictions
        net.setInput(blob)
        detections = net.forward()

        # Clear chart data for each frame
        chart_labels.clear()
        chart_accuracy.clear()

        for i in range(detections.shape[2]):
            # Extract the confidence (i.e., probability) associated with the prediction
            confidence = detections[0, 0, i, 2]

            if confidence > args["confidence"]:
                class_id = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype('int')

                # Draw bounding box for the object
                cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[class_id], 2)

                # Draw label and confidence of prediction in the frame
                label = "{}: {:.2f}%".format(CLASSES[class_id], confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                              COLORS[class_id], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[class_id], 2)

                # Write the label and confidence to the output file
                output_file.write(label + '\n')

                # Update chart data
                chart_labels.append(CLASSES[class_id])
                chart_accuracy.append(confidence * 100)

        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_chart():
    # Create a bar chart for accuracy levels
    plt.figure(figsize=(10, 6))
    plt.bar(chart_labels, chart_accuracy)
    plt.xlabel('Label')
    plt.ylabel('Accuracy (%)')
    plt.title('Object Detection Accuracy Levels')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('chart.png')  # Save the chart as an image

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Create a route to serve chart data as JSON
@app.route('/chart_data')
def chart_data():
    data = {'labels': chart_labels, 'accuracy': chart_accuracy}
    return jsonify(data)

@app.route('/chart')
def chart():
    return send_file('chart.png', mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
