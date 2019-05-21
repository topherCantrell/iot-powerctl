import mimetypes
import os

import tornado.ioloop
import tornado.web
import socket

import RPi.GPIO as GPIO

PIN_POWER_RELAY = 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_POWER_RELAY, GPIO.OUT, initial=GPIO.LOW)

CURRENT_RELAY_VALUE = False


# Let others on the network know about us
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('1.2.3.4', 80))
ip = s.getsockname()[0]
s.close()
notify = ('NOTIFY * HTTP/1.1\r\n' +
          'HOST: 239.255.255.250:1900\r\n' +
          'NTS: ssdp:alive\r\n' +
          'NT: upnp:rootdevice\r\n' +
          'UUID: ' + socket.getfqdn() + '\r\n' +
          'LOCATION: http://' + ip + '\r\n')
#print(notify)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
sock.sendto(notify.encode(), ('239.255.255.250', 1900))
sock.sendto(notify.encode(), ('239.255.255.250', 1900))

def set_power_switch_relay(value):
    global CURRENT_RELAY_VALUE
    if value:
        CURRENT_RELAY_VALUE = True
        # Turn the relay on (it is normally off)
        GPIO.output(PIN_POWER_RELAY, GPIO.HIGH)
    else:
        CURRENT_RELAY_VALUE = False
        # Turn the relay back off
        GPIO.output(PIN_POWER_RELAY, GPIO.LOW)


class PowerCheck(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.write(str(CURRENT_RELAY_VALUE))


class PowerHandler(tornado.web.RequestHandler):
    def get(self, state):
        if state.upper() == 'ON':
            set_power_switch_relay(True)
            #print('Relay ON')
        elif state.upper() == 'OFF':
            #print('Relay OFF')
            set_power_switch_relay(False)
        # Silently ignore anything else


# Just in case we are in a strange state
set_power_switch_relay(False)

mimetypes.add_type('text/javascript', '.js')

root = os.path.dirname(__file__)
cont = os.path.join(root, 'webroot')

handlers = [
    (r"/relay", PowerCheck),
    (r"/relay/([^/]*)", PowerHandler),
    (r"/(.*)", tornado.web.StaticFileHandler,
     {"path": cont, 'default_filename': 'index.html'}),
]

app = tornado.web.Application(handlers)
app.listen(80)

tornado.ioloop.IOLoop.current().start()
