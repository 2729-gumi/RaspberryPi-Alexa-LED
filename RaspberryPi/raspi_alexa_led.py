# -*- coding: utf-8 -*-

import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import pigpio
import json


# AWS IoT Core config
aws_iam_key = "XXXXXXXXXXXXXXXXXXXX"
aws_iam_secret_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
aws_endpoint = "xxxxxxxxxxxxxxxxxx.iot.us-west-2.amazonaws.com"
aws_region = "us-west-2"
aws_port = 443

aws_root_ca_path = "AmazonRootCA1.pem"

aws_topic_shadow = "$aws/things/RaspberryPiZero/shadow/update"
aws_topic_shadow_delta = "$aws/things/RaspberryPiZero/shadow/update/delta"


# Callback Function
def callback (_, userdata, message):
	print( "Topic:{}, Payload:{}".format(message.topic, message.payload) )
	
	obj = json.loads( message.payload )
	state = obj["state"]
	
	if "led" in state :
		led = state["led"]
		pig.write(17, led)
		print( "LED : {}".format(led) )
		report_led_state(led)

# Change Repoted Value
def report_led_state(led) :
	obj = { "state" :
			{ "reported" :
				{ "led" : led }
			}
		}
	client.publish(aws_topic_shadow, json.dumps(obj), 0)


# GPIO Initialization
pig = pigpio.pi()
pig.set_mode(17, pigpio.OUTPUT)

# Connect AWS IoT Core
client = AWSIoTMQTTClient("", useWebsocket=True)
client.configureIAMCredentials(aws_iam_key, aws_iam_secret_key)
client.configureCredentials(aws_root_ca_path)
client.configureEndpoint(aws_endpoint, aws_port)
client.connect()
client.subscribe(aws_topic_shadow_delta, 1, callback)

report_led_state(False)

try :
	while True :
		time.sleep(5)
except KeyboardInterrupt:
	pig.stop()
