from machine import Pin, PWM, time_pulse_us
import time
import network
import urequests
from time import sleep

# Wi-Fi setup
ssid = "TP-Link_E954"
password = "31225076"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected():
    print("Connecting to WiFi...")
    sleep(1)
print("Connected to WiFi")

# Telegram setup
Bot_token = "8330630060:AAFJCYjep8dhb-bHn3zni20BVOmWKNjfsgc"
chat_id = "1963912850"
msg = "Trash bin is full"
url = f"https://api.telegram.org/bot{Bot_token}/sendMessage?chat_id={chat_id}&text={msg}"

# Pins
trigger = Pin(18, Pin.OUT)
echo = Pin(21, Pin.IN)
servo1 = PWM(Pin(15), freq=50)
servo2 = PWM(Pin(4), freq=50)
RainSensor = Pin(5, Pin.IN)
ir = Pin(23, Pin.IN)
metal_sensor = Pin(22, Pin.IN)

SOUND_SPEED = 0.0343

def set_angle(servo, angle):
    duty = int((angle / 180) * 102 + 26)
    servo.duty(duty)
    sleep(1)

# Initialize servos
set_angle(servo1, 90)
set_angle(servo2, 90)

bin_full_notified = False

while True:
    # --- Ultrasonic distance measurement ---
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)

    try:
        duration = time_pulse_us(echo, 1, 30000)
        distance = (duration * SOUND_SPEED) / 2
    except OSError:
        distance = 999

    print("Distance:", distance, "cm")

    # --- Trash level detection ---
    if 5 <= distance < 25 and not bin_full_notified:
        print("🟢 Trash bin is full.")
        response = urequests.get(url)
        response.close()
        bin_full_notified = True
    elif distance > 25:
        bin_full_notified = False

    # --- Object classification ---
    if ir.value() == 0:
        print("Object detected")
        sleep(3)
        if metal_sensor.value() == 0:
            print("Metal detected")
            set_angle(servo2, 180)
            set_angle(servo1, 0)
            set_angle(servo1, 90)
            set_angle(servo2, 90)
        else:
            if RainSensor.value() == 0:
                print("Wet detected")
                set_angle(servo1, 0)
                set_angle(servo1, 90)
            else:
                print("Dry detected")
                set_angle(servo2, 0)
                set_angle(servo1, 0)
                set_angle(servo1, 90)
                set_angle(servo2, 90)

    sleep(0.5)