from flask import Flask, render_template
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

# MQTT Broker configuration
mqtt_broker = "test.mosquitto.org"
mqtt_port = 1883
mqtt_topic = "hospital/results"

# MQTT client setup
mqtt_client = mqtt.Client()

patient_data_list = []  # List to store all received patient data

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    global patient_data_list
    payload = json.loads(msg.payload.decode())
    patient_data_list.append(payload)
    print("Received message:", payload)  # Debugging statement

# Set MQTT callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

@app.route('/')
def index():
    global patient_data_list
    return render_template('doctor_dashboard.html', patient_data_list=patient_data_list)

if __name__ == '__main__':
    app.run(debug=True)
