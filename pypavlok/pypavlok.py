import logging
from gattlib import DiscoveryService, GATTRequester

class PyPavlok(GATTRequester):
    '''Bluetooth controller for Pavlok
    Subclasses GATTRequester to send GATT requests to device
    '''
    #UUIDs of exposed GATT services
    service_uuids = {
        'shock' : '6e9d7a34-ddc0-4b47-9df4-fc45d2891827',
        'vibration' : '7eca7033-fc71-4a58-8775-225e813a03fb',
        'beep' : 'efd6fd9d-681b-4f19-9121-59900f57a401',
        'led' : '0102a282-7f71-4d53-85d4-c5f039491de5',
        'battery_level' : '00002a19-0000-1000-8000-00805f9b34fb',
        'hardware_revision' : '00002a27-0000-1000-8000-00805f9b34fb',
        'firmware_revision' : '00002a26-0000-1000-8000-00805f9b34fb'
    }

    def __init__(self, addr=None, device='hci0', debug=False, **connect_kwargs):
        '''
        @param addr (optional): MAC address of Pavlok device
                                If not passed, will be discovered with DiscoveryService (requires root privileges)
        @param device (optional): host Bluetooth interface ('hci0' by default)
        @param debug (optional): debug logging (disabled by default)
        @param connect_kwargs: keyword arguments (security_level, channel_type, mtu, psm) to pass to GATTRequester.connect
                               security_level: 'low' (default), 'medium', 'high'
                               channel_type: 'public' (default), 'random'
                               mtu: integer
                               psm: integer
        '''
        self._init_logging(debug)

        if not addr:
            addr = self._get_pavlok_mac_addr(device)
            assert addr, 'Could not find Pavlok device'

        GATTRequester.__init__(self, addr, False, device) #GATTRequester is an old-style class
        if connect_kwargs:
            self.logger.debug('Got keyword arguments for self.connect: %s', connect_kwargs)
        self.connect(wait=False, **connect_kwargs) #Blocking connect() is better, but it would require root privileges
        self._wait_until_connected()

        characteristics = self.discover_characteristics()
        self.logger.debug('GATT characteristics: %s', characteristics)
        #Find matching value handles for service UUIDs
        self.handles = {name:filter(lambda e: e['uuid'] == uuid, characteristics)[0]['value_handle']\
                        for name, uuid in self.service_uuids.items()}
        self.logger.debug('GATT value handles: %s', self.handles)
        self.logger.debug('Hardware revision: %s, firmware revision: %s', self.hardware_revision, self.firmware_revision)

    @property
    def battery_level(self):
        'Battery level in percents'
        return ord(self.read_by_handle(self.handles['battery_level'])[0])

    def shock(self, level=50, count=1, duration_on=1000, duration_off=1000):
        '''Shock the user
        All action methods (shock, vibrate, beep and led) share common parameters:
        @param level: level of action in percents
        @param count: number of repetitions
        @param duration_on: duration of action in milliseconds (<= 5 sec)
        @param duration_off: if count > 0, set the interval between repetitions in milliseconds (<= 5 sec)
        '''
        (level, duration_on, duration_off) = self._process_args(duration_on, duration_off, level)
        self.write_array_by_handle(self.handles['shock'], [count, level, duration_on, duration_off])

    def vibrate(self, level=50, count=1, duration_on=1000, duration_off=1000):
        '''Vibrate, see docstring of shock
        @param level: here it means speed of vibration
        '''
        (level, duration_on, duration_off) = self._process_args(duration_on, duration_off, level)
        self.write_array_by_handle(self.handles['vibration'], [count, level, duration_on, duration_off])

    def beep(self, level=50, count=1, duration_on=1000, duration_off=1000):
        '''Beep, see docstring of shock
        @param level: here it means tone frequency
        '''
        (level, duration_on, duration_off) = self._process_args(duration_on, duration_off, level)
        self.write_array_by_handle(self.handles['beep'], [count, level, duration_on, duration_off])

    def led(self, led1=True, led2=True, count=1, duration_on=1000, duration_off=1000):
        '''Blink LEDs
        @param led1: Blink yellow LED
        @param led2: Blink red LED
        Other params are the same as in shock, except level, which is not used
        '''
        (level, duration_on, duration_off) = self._process_args(duration_on, duration_off)

        led_mask = 0
        if led1:
            led_mask |= 2
        if led2:
            led_mask |= 8

        self.write_array_by_handle(self.handles['led'], [count, level, duration_on, duration_off, led_mask])

    @property
    def firmware_revision(self):
        'Pavlok firmware revision'
        return self.read_by_handle(self.handles['firmware_revision'])[0]

    @property
    def hardware_revision(self):
        'Pavlok hardware revision'
        return self.read_by_handle(self.handles['hardware_revision'])[0]

    def _process_args(self, duration_on, duration_off, level=100):
        'Encode parameters into the form suitable for device'
        from math import floor
        level = int(floor(level * 2.55)) #100% -> 0xff, 50% -> 0x32 etc
        duration_on = int(duration_on / 20)
        duration_off = int(duration_off / 20)
        return (level, duration_on, duration_off)

    def write_array_by_handle(self, handle, *args):
        'Handy to pack list of arguments into a byte string and send it into the handle'
        data = str(bytearray(*args))
        self.logger.debug('write array: handle: %d, args: %s, encoded data: %s', handle, args, ''.join(['%02x' % ord(c) for c in data]))
        self.write_by_handle(handle, data)

    def _wait_until_connected(self):
        '''Wait until connected. After 10 attempts throws an exception
        '''
        from time import sleep
        for _ in range(20):
            if self.is_connected():
                break
            else:
                sleep(0.5)
        else:
            raise RuntimeError('Cannot connect')

    def _init_logging(self, enable_debug):
        'Initialize logger'
        if not logging.root.handlers:
            logging.basicConfig()
        self.logger = logging.getLogger('pypavlok')
        self.logger.setLevel(logging.DEBUG if enable_debug else logging.INFO)

    def _get_pavlok_mac_addr(self, device):
        'Find Pavlok, return its MAC address'
        service = DiscoveryService(device)
        devices = service.discover(3) #3 seconds timeout
        for addr, name in devices.items():
            if name.startswith('Pavlok'):
                self.logger.debug('Found Pavlok with MAC address %s', addr)
                return addr
