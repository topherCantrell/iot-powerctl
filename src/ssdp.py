# Very minimal implementation for SSDP alive broadcasts

import socket
import struct
import sys


MCAST_GRP = '239.255.255.250'
MCAST_PORT = 1900
MULTICAST_TTL = 2
IS_ALL_GROUPS = True


def send_alive():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.2.3.4', 80))
    ip = s.getsockname()[0]
    s.close()
    notify = ('NOTIFY * HTTP/1.1\r\n' +
              'HOST: {}:{}\r\n'.format(MCAST_GRP, MCAST_PORT) +
              'NTS: ssdp:alive\r\n' +
              'NT: upnp:rootdevice\r\n' +
              'UUID: ' + socket.getfqdn() + '\r\n' +
              'LOCATION: http://' + ip + '\r\n')
    print(notify)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    # Protocol recommends sending two
    sock.sendto(notify.encode(), (MCAST_GRP, MCAST_PORT))
    sock.sendto(notify.encode(), (MCAST_GRP, MCAST_PORT))


def print_notifies():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if IS_ALL_GROUPS:
        # on this port, receives ALL multicast groups
        sock.bind(('', MCAST_PORT))
    else:
        # on this port, listen ONLY to MCAST_GRP
        sock.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        print(sock.recv(10240))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'send':
        send_alive()
    else:
        print_notifies()
