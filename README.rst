========
pypavlok
========

Unofficial Python Bluetooth Pavlok API

Official `Pavlok API <https://github.com/EastCoastProduct/pavlokjs>`_ makes requests to cloud service to send message to your tablet which will send Bluetooth command to your device. Maybe it works for tablet apps, but it is a quite clumsy way to zap people. 

This package controls Pavlok directly with Bluetooth commands. 

--------------
Requirements
--------------
* Bluetooth 4 compatible adapter (Pavlok uses Bluetooth Low Energy)
* Bluez
* gattlib to interface gatttool
* Python 2.7
* Linux (I haven't tested the code with anything else)

--------------
Installation
--------------
Use pip:
    pip install pypavlok

Be sure to install gattlib dependencies: boost-python, boost-thread and glib2

--------------
Usage
--------------
>>> from pypavlok import PyPavlok
>>> pavlok = PyPavlok() #If MAC address is not specified, it will be found using service discovery (requires root privileges)
>>> pavlok = PyPavlok('00:07:80:B5:9A:31', 'hci0') #Or pass MAC address (doesn't require special permissions)
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

All action methods (shock, vibrate, led, beep) share common set of parameters:

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

    <device name> hci0:   Type: BR/EDR  Bus: USB

    <device status> DOWN


If the status is down, run:

.. code-block:: console

    $ sudo hciconfig <device name> up


Search for BLE devices:

.. code-block:: console

    $ sudo hcitool lescan

    LE Scan ...

    <MAC address like xx:xx:xx:xx:xx:xx> Pavlok-xxxx

    Ctrl-C


Try to connect to Pavlok with gatttool:

.. code-block:: console

    $ gatttool -b <MAC address> -I

    [<MAC address>][LE]> connect

    Attempting to connect to <MAC address>

    Connection successful

    [<MAC address>][LE]> primary

    attr handle: 0x0001, end grp handle: 0x0007 uuid: 00001800-0000-1000-8000-00805f9b34fb

    attr handle: 0x0008, end grp handle: 0x001a uuid: 0000180a-0000-1000-8000-00805f9b34fb


If you got to this point, everything should work

If you encounter problems with Pavlok, try pressing The Zap Button for about 15 seconds -- it will blink, vibrate and reset
