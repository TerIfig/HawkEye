import json
import base64
import calendar
import time
import os
from ibm_watson import VisualRecognitionV3
import paho.mqtt.client as mqtt

input_directory = "C:\\Users\\ydidier\\Documents\\Watson\\pictures\\"		
"""
JSON Dumps Encoder
"""
class MyEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__

"""
IBM Watson Visual Recognition Object
"""
visual_recognition = VisualRecognitionV3(
    version    = '2018-03-19',
    iam_apikey = 'K8-xMjYk_BdKRR5DqrVKovBmso4Icxi7QEv3nVTEGo-f',
)

"""
MQTT Subscription
"""
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("incoming/snap/#")

    

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
	###########################################################################
	# Here we have to code the extraction of the image metadata (geolocation) #
	###########################################################################
    # Sends the image to Watson
    with open(input_directory+"image.jpg", 'rb') as iot_image:
        response = visual_recognition.classify(iot_image, threshold=0.0, owners=["me"])
        response_dump = json.dumps(response, cls=MyEncoder, indent=2)
        parser = json.loads(response_dump)
        print("Image sent to Watson!")
        # Flood Class
        image_class = parser["result"]["images"][0]["classifiers"][0]["classes"][0]["class"]
        # Flood Level
        image_score = str(parser["result"]["images"][0]["classifiers"][0]["classes"][0]["score"])
        timestamp = calendar.timegm(time.gmtime())
        print(image_score)
        if float(image_score) > 0.6:
            print("Image has score greater than 0.6. Alert sent to the chat!")
            client.publish("users/chatbot_hawkeye", payload="{\"timestamp\":\"" + str(timestamp) + "\"}", qos=0, retain=False)
        #    client.publish("chat", payload="{\"clientId\":\"chatbot_hawkeye\",\"textReply\":\"Flood Alert!\"}", qos=0, retain=False)
            client.publish("chat", payload="{\"clientId\":\"chatbot_hawkeye\",\"textReply\":\"Flood Alert! Latitude 17.419310, Longitude 78.337980\"}", qos=0, retain=False)
        os.remove(input_directory+"image.jpg")
	

client = mqtt.Client("HawkEyes")
client.on_connect = on_connect
client.on_message = on_message

client.connect("frparvm-ion01", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()