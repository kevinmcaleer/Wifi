# 
# Raspberry Pi Pico Wifi Module
# Kevin McAleer
# August 2021
#
# This file will connect to the wifi network detailed in the secret.py file
# It will also connect to the MQTT server and topic listed below
# Any messages sent to it over from the Pico via serial will be sent to the MQTT topic
# Any messages from the MQTT server will be passed to the pico via serial

from secret import wifi_password, wifi_ssid, mqtt_server_ip
from time import sleep
from umqttsimple import MQTTClient
import ubinascii
import machine
from machine import UART, Pin
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()
import uos

uos.dupterm(None,1)
ssid = wifi_ssid
password = wifi_password
mqtt_server = mqtt_server_ip
client_id = ubinascii.hexlify(machine.unique_id())

topic_sub = b'pico' 
topic_pub = b'pico' 

def sub_cb(topic, msg):
    print("new message")
    print((topic, msg))
    
    # send message to serial
    myserial.write(msg)

def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    print(client_id, mqtt_server, topic_sub)
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

def restart_reconnect():
    print('Failed to connect to MQTT broker, Reconnecting...')
    time.sleep(10)
    machine.reset()



print("Wifi Device Online")

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())


print("setting up serial")
sleep(1)
# Setup Serial
rx_pin = Pin(1)
tx_pin = Pin(0)

myserial = UART(0, 9600)
myserial.init(9600)
print("Serial setup complete")


    
try:
    client = connect_and_subscribe()
except OSError as e:
    restart_reconnect()

client.publish(topic_pub, b"Pico Wifi Online")
while True:
    try:
        client.check_msg()
        # client.publish(topic_pub, msg)
        
        if myserial.any() > 0:
            print("reading message from serial")    
            msg = myserial.readline()
            print("msg: ", msg)
            client.publish(topic_pub, msg)
            time.sleep(0.1)
    except OSError as e:
        restart_reconnect()
