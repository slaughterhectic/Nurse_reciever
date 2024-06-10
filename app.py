from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, flash
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flash messages

# MQTT Broker configuration
mqtt_broker = "test.mosquitto.org"
mqtt_port = 1883
mqtt_topic = "hospital/results"
mqtt_feedback_topic = "hospital/feedback"

# MQTT client setup
mqtt_client = mqtt.Client()

patient_data_list = []  # List to store all received patient data
messages = []  # List to store all feedback messages

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe([(mqtt_topic, 0), (mqtt_feedback_topic, 0)])

def on_message(client, userdata, msg):
    global patient_data_list, messages
    if msg.topic == mqtt_topic:
        payload = json.loads(msg.payload.decode())
        patient_data_list.append(payload)
        print("Received patient data:", payload)  # Debugging statement
    elif msg.topic == mqtt_feedback_topic:
        feedback_message = msg.payload.decode()
        messages.append(feedback_message)
        print("Received feedback message:", feedback_message)  # Debugging statement

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

@app.route('/')
def index1():
    global patient_data_list, messages
    patient_ids = [data['patient_id'] for data in patient_data_list]
    return render_template('index1.html', patient_ids=patient_ids, messages=messages)

@app.route('/patient/<patient_id>')
def patient_details(patient_id):
    global patient_data_list
    patient_data = next((data for data in patient_data_list if data['patient_id'] == patient_id), None)
    return render_template('patient_details.html', patient_data=patient_data)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    result = mqtt_client.publish(mqtt_feedback_topic, message)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        flash('Message sent successfully!', 'success')
    else:
        flash('Failed to send message', 'danger')
    return redirect(url_for('index1'))

if __name__ == '__main__':
    app.run(debug=True)
