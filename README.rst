========
pypavlok
========

Unofficial Python Bluetooth controller module for Pavlok

Official `Pavlok API <https://github.com/EastCoastProduct/pavlokjs>`_ makes requests to cloud service to send message to your tablet which will send Bluetooth command to your device. Maybe it works for tablet apps, but it is a quite clumsy way to zap people.

--------------
Requirements
--------------
* Bluetooth 4 compatible adapter (Pavlok uses Bluetooth Low Energy)
* Bluez
* gattlib to interface gatttool

  Be sure to install boost-python, boost-thread and glib2 as its dependencies
* Python 2.7
* Linux 

  I haven't tested with anything else

--------------
Usage
--------------
>>> from pypavlok import PyPavlok
>>> mac_addr = '00:07:80:B5:9A:31' #MAC address of your Pavlok
>>> pavlok = PyPavlok(mac_addr, 'hci0') #MAC addr and Bluetooth interface name, hci0 is a default value
>>> pavlok.battery_level
95
>>> pavlok.shock()
>>> pavlok.shock(level=50) #50% discharge
>>> pavlok.beep()
>>> pavlok.beep(count=3, duration_on=200, duration_off=100) #3 beeps by 0.2 sec with interval 0.1 sec
>>> pavlok.led()
>>> pavlok.led(led1=False, led2=True, count=5, duration_off=300) #Blink with red LEDs 5 times by 1 sec with interval 0.3 sec
>>> pavlok.vibrate()
>>> pavlok.firmware_revision
'2.4.28'

All action methods (shock, vibrate, led, beep) have common set of parameters:
* level: discharge percents for shock(), tone for beep(), vibration speed for vibrate(), not used in led(). Default: 50
* count: number of repetitions. Default: 1
* duration_on: duration of action in milliseconds (<= 5 sec). Default: 1 sec
* duration_off: if count > 0, set the interval between repetitions in milliseconds (<= 5 sec). Default: 1 sec

--------------------
Checking your setup
--------------------
Check if your bluetooth adapter is up:
.. code-block:: console

$ sudo hciconfig

<device name> *hci0*>:   Type: BR/EDR  Bus: USB

...

<device status> *DOWN*

If it's down run:
::
$ sudo hciconfig <device name>

Search for BLE devices:

$ sudo hcitool lescan

LE Scan ...

<MAC address like xx:xx:xx:xx:xx:xx> Pavlok-xxxx

Ctrl-C


Try to connect to Pavlok with gatttool:
::
$ gatttool -b <MAC address> -I

[<MAC address>][LE]> connect

Attempting to connect to <MAC address>

Connection successful

[<MAC address>][LE]> primary

attr handle: 0x0001, end grp handle: 0x0007 uuid: 00001800-0000-1000-8000-00805f9b34fb

attr handle: 0x0008, end grp handle: 0x001a uuid: 0000180a-0000-1000-8000-00805f9b34fb

...

If you got to this point, everything should work

If you encounter problems with Pavlok, try pushing The Zap Button for about 15 seconds -- it will blink, vibrate and reset