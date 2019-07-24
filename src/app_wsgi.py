import cgi
import json

#import RPi.GPIO as GPIO
import ssdp


ssdp.send_alive()

PIN_POWER_RELAY = 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_POWER_RELAY, GPIO.OUT, initial=GPIO.LOW)

CURRENT_RELAY_VALUE = False


def set_power_switch_relay(value):
    global CURRENT_RELAY_VALUE
    CURRENT_RELAY_VALUE = value
    if value:
        pass
        GPIO.output(PIN_POWER_RELAY, GPIO.HIGH)
    else:
        pass
        GPIO.output(PIN_POWER_RELAY, GPIO.LOW)
    print(value)


def _do_static(environ, start_response):
    try:
        fn = environ['PATH_INFO']
        if fn == '/':
            fn = '/index.html'
        #print('*', fn, '*')
        with open('webroot/' + fn, 'rb') as f:
            data = f.read()
        if fn.endswith('.css'):
            start_response('200 OK', [('Content-Type', 'text/css')])
        elif fn.endswith('.js'):
            start_response('200 OK', [('Content-Type', 'text/js')])
        else:
            start_response('200 OK', [('Content-Type', 'text/html')])
        return [data]
    except:
        start_response('404 Not found', [('Content-Type', 'text/html')])
        return [b'']


def application(environ, start_response):

    path = environ['PATH_INFO']
    if not path.startswith('/relay'):
        return _do_static(environ, start_response)

    if path.endswith('/on'):
        set_power_switch_relay(True)

    elif path.endswith('/off'):
        set_power_switch_relay(False)

    else:
        pass
        # Ignore

    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [str(CURRENT_RELAY_VALUE).encode()]


if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        try:
            httpd = make_server('', 80, application)
            print('Serving on port 80...')
        except:
            httpd = make_server('', 8080, application)
            print('Serving on port 8080...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
