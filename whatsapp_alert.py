import time
import pywhatkit as pwk

# Function to send a WhatsApp alert
def send_whatsapp_alert():
    phone_number = "+919791933796"  # Replace with the target WhatsApp number
    message = "Your cattle is detected...!!!" # Customize the message
    pwk.sendwhatmsg(phone_number, message, time.localtime().tm_hour, time.localtime().tm_min + 2)  # Send the message after 2 minutes

# Simulate detection
def simulate_detection():
    # In a real scenario, you would have code here to detect a cow with its confidence level
    # For demonstration purposes, let's assume a simulated detection with confidence > 95%
    confidence = 96.0
    if confidence > 95.0:
        send_whatsapp_alert()  # Send a WhatsApp alert if cow is detected with confidence > 95%

# Continuously monitor the detection
while True:
    simulate_detection()
    time.sleep(60)  # Wait for 1 minute before checking again