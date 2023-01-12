#!/usr/bin/env python3
"""
Plug easy configurator
thanks to bl0x
https://github.com/bl0x/ghomapy
"""

#import sys
import argparse
import socket
from time import sleep
import logging


parser = argparse.ArgumentParser()
parser.add_argument("plugip", help="G-Homa plug IP default 10.10.100.254")

parser.add_argument("ctrlhost", help="your controller server of G-Homa")

parser.add_argument("ctrlport", help="your controller server port of G-Homa, default 4196",
                    type=int)


parser.add_argument("ssid", help="your SSID which shoul G-Homa Plug connect")

parser.add_argument("pskey", help="your WiFI passwod")

args = parser.parse_args()

# Setup
#ctrlhost = "172.16.1.184" # your control server IP address
#ctrlport = 4196           # port on the control server (default: 4196)

plugip = args.plugip
ctrlhost = args.ctrlhost
ctrlport = args.ctrlport
ssid = args.ssid
pskey = args.pskey



plugport = 48899      # udp port of G-Homa


hello = "HF-A11ASSISTHREAD"
init = "+ok"



sleeptime=0.2

initcmds = [ hello, init ]

# config net
#cmds = [ f"AT+WSSSID={ssid}", f"AT+WSKEY=WPA2PSK,AES,{pskey}", "AT+WMODE=sta", f"AT+NETP=TCP,Client,{ctrl}, {port}" ]
usercmds = [ "AT+WSSSID=%s"%(ssid), "AT+WSKEY=WPA2PSK,AES,%s"%(pskey), "AT+WMODE=sta", "AT+NETP=TCP,Client,%s,%s"%(ctrlport, ctrlhost), "AT+Z" ]
#usercmds = [ "AT+WSSSID=%s"%(ssid), "AT+WSKEY=WPA2PSK,AES,%s"%(pskey), "AT+WMODE=sta", "AT+NETP=TCP,Client,%s,%s"%(ctrlport, ctrlhost) ]

# getinfo
#usercmds= [ 'AT+WSSSID', 'AT+NETP', 'AT+VER']

# reset factory defaults:
#usercmds= [ 'AT+RELD']

# restart
#usercmds= [ 'AT+Z']

cmds= initcmds + usercmds


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 48899))
sock.settimeout(2.0)

def send(msg):
	_LOGGER.info('Sending: %s',msg)
	sock.sendto(msg.encode('utf-8'), (plugip, plugport))

def recv():
    while True:
        data, addr = sock.recvfrom(1024)
        text = data.decode('ascii')
        _LOGGER.debug('Received data from addr %s',addr)
        if text.strip() != '+ERR=-1':
            _LOGGER.info('data = %s',text.strip())
            return text
        else:
            _LOGGER.warn('data = %s',text.strip())
            return text


_LOGGER = logging.getLogger("ghoma configurator")


if __name__ == "__main__":

    """ init configure logging """
    logging.basicConfig()
    #_LOGGER.setLevel(logging.DEBUG)
    _LOGGER.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.StreamHandler()
    log.setFormatter(formatter)
    _LOGGER.addHandler(log)
    _LOGGER.propagate=0

    """ init communication """
    _LOGGER.info("*** Init Communication to the Plug ***")


    for cmd in cmds:
        retry=3
        while retry>0:
            try:
                if cmd in initcmds:
                    _LOGGER.info("Sending init cmd")
                    send(cmd)
                else:
                    _LOGGER.info("Sending user cmd")
                    send(cmd+'\r')
                if cmd != 'AT+Z' and cmd !='+ok':
                    recv()
                retry=-1
            except socket.timeout:
                retry-=1
                if retry==0:
                    _LOGGER.error("Reading timout, try restart Plug")
                    cmds=[]
                else:
                    _LOGGER.error("Reading timout, retry %s",retry)
            except Exception:
                retry-=1
                _LOGGER.error("Reading error")
                #return
        if retry==0:
            break
        else:
            continue
        sleep(sleeptime)
