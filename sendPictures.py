import json
import base64
import calendar
import time
import os
import paho.mqtt.client as mqtt

input_directory = "C:\\Users\\ydidier\\Documents\\Watson\\pictures\\"		
"""
JSON Dumps Encoder
"""
class MyEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__


"""
MQTT Subscription
"""
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("incoming/snap/#")
    with open(input_directory+"flood.jpg", "rb") as flood_image:
        encoded_flood_image = base64.b64encode(flood_image.read())
        client.publish("incoming/snap/india01", payload=encoded_flood_image)
    
    print("Images published!")
    

"""
IOT messages treatment
"""
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    encoded_image = msg.payload
    # Stores the image
    with open(input_directory+"image.jpg", "wb") as iot_image:
        iot_image.write(base64.decodebytes(encoded_image))
    print("Image received!")

	

client = mqtt.Client("camera")
client.on_connect = on_connect
client.on_message = on_message

client.connect("frparvm-ion01", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.


client.loop_forever()