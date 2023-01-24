#!/usr/bin/env python3
"""
g-homa2mqtt server
thanks to:  poldy79
https://github.com/poldy79/ghoma2mqtt
"""
import sys
import logging
import socketserver
import time
import socket
import json
import ssl
import paho.mqtt.client as mqtt


_LOGGER = logging.getLogger("ghoma2mqtt")

MQTTHOST=sys.argv[1] #str IPka
MQTTPORT=int(sys.argv[2]) #int port
if sys.argv[3] == "true":
    MQTTSSL=True
else:
    MQTTSSL=False

USERNAME=sys.argv[4] #str
PASSWORD=sys.argv[5] #str

# RETAIN
if sys.argv[6] == "true":
    RETAIN=True
else:
    RETAIN=False

# AUTODISCOVERY
if sys.argv[7]== "true":
    AUTODISCOVERY=True
else:
    AUTODISCOVERY=False

# DISCOVERYTOPIC
if sys.argv[8]=="":
    DISCOVERYTOPIC="homeassistant"
else:
    DISCOVERYTOPIC=sys.argv[8] #str

# DEBUG
if sys.argv[9] == "true":
    DEBUG=True
else:
    DEBUG=False

# helper - pre evidenciu zastrciek v registracii
PLUG_REGISTERING=[]



def print_hex(my_hex):
    """ print hex value"""
    if isinstance(my_hex,str):
        new_hex=" ".join(hex(ord(n)) for n in my_hex)
    if isinstance(my_hex,list):
        result = []
        for i in my_hex:
            result.append("0x%1x"%(i))
        new_hex=",".join(result)
    return new_hex

class InvalidMsg(Exception):
    """ invalid msg """
    def __init__(self,err):
        self.err = err
        #pass


class GhomaMsgEncode():
    """ encode msg """
    def __init__(self,cmd,payload,mode=0):
        self.msg = bytearray(b"\x5a\xa5")
        self.msg+=bytes([mode])
        self.msg+=bytes([len(payload)+1])
        self.msg+=bytes([cmd])
        checksum = 0xff-cmd
        for i in payload:
            self.msg+=bytes([i])
            checksum-=i
            if checksum <0:
                checksum+=256
        self.msg+=bytes([checksum])
        self.msg+=b"\x5b\xb5"

class GhomaMsgDecode():
    """ decode msg """
    def __init__(self,msg):
        if not msg.hex()[0:4]=="5aa5":
            raise InvalidMsg("Invialid prefix")
            
        self.mode = msg[2]
        self.length = msg[3]-1
        self.cmd = msg[4]
        self.payload = []
        checksum = 0xff-self.cmd
        for i in range(self.length):
            self.payload.append(msg[5+i])
            checksum-=msg[5+i]
            if checksum < 0:
                checksum+=256
        if not checksum == msg[5+self.length]:
            raise InvalidMsg("Invalid checksum")
        if not msg[6+self.length:].startswith(b"\x5b\xb5"):
            _LOGGER.warning("print_hex: %s",hex)
            raise InvalidMsg("Invalid postfix")
        self.next = msg[8+self.length:] 


class ThreadedEchoRequestHandler(
        socketserver.BaseRequestHandler,
    ):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def publish_state(self):
        """ public state to mqtt"""
        topic = f"ghoma/{self.full_mac_str}/state"
        self.client.publish(topic, self.state,retain=RETAIN)
        self.client.publish("ghoma",self.full_mac_str,retain=RETAIN)

    def mqtt_discovery_config(self):
        """ create mqtt discovery config """

        discovery_conf_topic=f"{DISCOVERYTOPIC}/switch/ghoma/{self.short_mac_name}/config"

        config_record= {
            "name": f"MQTT switch ghoma_{self.short_mac_name}",
            "state_topic": f"ghoma/{self.full_mac_str}/state",
            "command_topic": f"ghoma/{self.full_mac_str}/set",
            "device_class": "outlet",
            "unique_id": f"ghoma_{self.short_mac_name}",
            "payload_on": "ON",
            "payload_off": "OFF",
            "state_on": "ON",
            "state_off": "OFF",
            "retain": True,
            "device": {
                "identifiers": [
                    f"ghoma_{self.short_mac_name}"
                ],
                "manufacturer": "G-Homa",
                "model": "G-Homa Generic",
                "name": f"G-Homa SmartPlug {self.short_mac_name}"
            }
        }
        _LOGGER.debug("MQTT autodiscover register device G-Homa SmartPlug %s",self.short_mac_name)
        self.client.publish(discovery_conf_topic, json.dumps(config_record),retain=RETAIN)

    def handle(self):
        def on_message(client, userdata, msg):
            if msg.payload == b"1" or msg.payload.lower()==b"on":
                _LOGGER.debug("Plug ID: %s MQTT request turn ON",self.short_mac_name)
                payload=[0x01,0x01,0x0a,0xe0]+self.triggercode+self.short_mac+[0xff,0xfe,0x00,0x00,0x10,0x11,0x00,0x00,0x01,0x00,0x00,0x00,0xff]
                self.request.sendall(GhomaMsgEncode(cmd=0x10,payload=payload).msg)
            elif msg.payload == b"0" or msg.payload.lower()==b"off":
                _LOGGER.debug("Plug ID: %s MQTT request turn OFF",self.short_mac_name)
                payload=[0x01,0x01,0x0a,0xe0]+self.triggercode+self.short_mac+[0xff,0xfe,0x00,0x00,0x10,0x11,0x00,0x00,0x01,0x00,0x00,0x00,0x00]
                self.request.sendall(GhomaMsgEncode(cmd=0x10,payload=payload).msg)
        
        def on_connect(client, userdata, flags, rc):
            _LOGGER.info("Connected to MQTT broker")
            self.client.subscribe(f"ghoma/{self.full_mac_str}/set")
        
        self.state = "unknown"
        self.triggercode = [ 0x32,0x23 ]

        self.full_mac =[]
        self.short_mac =[]

        self.full_mac_str = "00:00:00:00:00:00"
        self.short_mac_str="" #as hex string
        self.short_mac_name="" # name based on mac
        
        self.client = mqtt.Client()
        self.client.username_pw_set(USERNAME, PASSWORD)

        #self.client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
        #                tls_version=ssl.PROTOCOL_TLS, ciphers=None)

        if MQTTSSL:
            self.client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE,
                        tls_version=ssl.PROTOCOL_TLS, ciphers=None)

        self.client.connect(host=MQTTHOST,port=MQTTPORT)
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.loop_start()

        _LOGGER.debug("Sending Init 1 Part 1, CMD: %s, Payload: 0x05,0x0d,0x07,0x05,0x07,0x12", hex(2))
        self.request.sendall(GhomaMsgEncode(cmd=2,payload=[0x05,0x0d,0x07,0x05,0x07,0x12]).msg)
        _LOGGER.debug("Sending Init 1 Part 2, CMD: %s",hex(2))
        self.request.sendall(GhomaMsgEncode(cmd=2,payload=[]).msg)
        _LOGGER.debug("Sending Init 2 CMD: %s Payload: 0x01", hex(5))
        self.request.sendall(GhomaMsgEncode(cmd=5,payload=[0x01]).msg)
        alive = time.time()
        while True:
            try:
                self.data = self.request.recv(1024)
            except Exception as ex:
                _LOGGER.debug(ex)
                return
            if len(self.data) == 0:
                time.sleep(.1)
                if time.time() - alive > 30:
                    _LOGGER.debug("Timeout exceeded!")
                    return
                continue
            while not len(self.data) == 0:
                msg = GhomaMsgDecode(self.data)

                # init 1 packet
                if msg.cmd == 0x03:
                    self.short_mac=msg.payload[5:8]
                    self.short_mac_name="".join("%02x"%(n) for n in self.short_mac)
                    self.triggercode=msg.payload[3:5]
                    _LOGGER.debug("Plug ID: %s Received Init 1 reply, CMD: %s Payload: %s",self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                    _LOGGER.debug("Sending Init 2 to Plug ID: %s, CMD: 0x05 Payload: 0x01", self.short_mac_name)
                    self.request.sendall(GhomaMsgEncode(cmd=0x05,payload=[0x01]).msg)

                # keepalive - heartbeat packet
                elif msg.cmd == 0x04:
                    self.short_mac=msg.payload[5:8]
                    self.short_mac_name="".join("%02x"%(n) for n in self.short_mac)
                    _LOGGER.debug("Plug ID: %s Recieved Alive, CMD: %s Payload: %s",self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                    _LOGGER.debug("Sending Alive Response to Plug ID: %s, CMD: 0x06", self.short_mac_name)
                    self.request.sendall(GhomaMsgEncode(cmd=0x06,mode=1,payload=[]).msg)
                    self.publish_state()


                # init 2 packet
                elif msg.cmd==0x07:
                    if len(msg.payload)==17:
                        self.short_mac=msg.payload[5:8]
                        self.short_mac_name="".join("%02x"%(n) for n in self.short_mac)
                        self.full_mac=msg.payload[-6:]
                        self.full_mac_str= ":".join("%02x"%(n) for n in self.full_mac)
                        _LOGGER.debug("Plug ID: %s Full MAC: %s",self.short_mac_name, self.full_mac_str)
                        _LOGGER.debug("Plug ID: %s Recieved Init 2 part 1 reply, CMD: %s Payload: %s",self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                    elif len(msg.payload)==16:
                        self.short_mac=msg.payload[5:8]
                        self.short_mac_name="".join("%02x"%(n) for n in self.short_mac)
                        if (self.full_mac[-3:]==self.short_mac):
                            _LOGGER.info("Plug ID: %s registered OK",self.short_mac_name)
                            PLUG_REGISTERING.append(self.short_mac_name)
                            _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                            self.mqtt_discovery_config()
                            self.publish_state()
                            self.client.subscribe(f"ghoma/{self.full_mac_str}/set")
                        else:
                            _LOGGER.warning("Plug ID: %s Recieved Init 2 part 1 reply NOT OK, CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                                   
                # set switch state packet
                elif msg.cmd==0x90:
                    self.short_mac=msg.payload[5:8]
                    self.short_mac_name="".join("%02x"%(n) for n in self.short_mac)
                         
                    # physical button press
                    if msg.payload[19]==0x00 and msg.payload[11]==0x81:
                        if self.short_mac_name in PLUG_REGISTERING:
                            _LOGGER.info("PLUG ID: %s Initialization Done", self.short_mac_name)
                            PLUG_REGISTERING.remove(self.short_mac_name)
                        else:
                            _LOGGER.info("PLUG ID: %s Someone pressed the switch from on->off", self.short_mac_name)

                        _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                        self.state = "OFF"
                        self.publish_state()
                    elif msg.payload[19]==0xff  and msg.payload[11]==0x81:
                        if self.short_mac_name in PLUG_REGISTERING:
                            _LOGGER.info("PLUG ID: %s Initialization Done", self.short_mac_name)
                            PLUG_REGISTERING.remove(self.short_mac_name)
                        else:
                            _LOGGER.info("PLUG ID: %s Someone pressed the switch from off->on", self.short_mac_name)

                        _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                        self.state = "ON"
                        self.publish_state()
                    # alarm / 3s physical button pres+hold
                    elif msg.payload[19]==0x1  and msg.payload[11]==0x81:
                        _LOGGER.info("Plug ID: %s ALARM",self.short_mac_name)
                        _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))

                    # network switch 
                    elif msg.payload[19]==0x00  and msg.payload[11]==0x11:
                        _LOGGER.info("Plug ID: %s Switch OFF",self.short_mac_name)
                        _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                        self.state = "OFF"
                        self.publish_state()
                    elif msg.payload[19]==0xff  and msg.payload[11]==0x11:
                        _LOGGER.info("Plug ID: %s Switch ON",self.short_mac_name)
                        _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                        self.state = "ON"
                        self.publish_state()
                    else:
                        _LOGGER.warning("Plug ID: %s Unknown CMD %s Payload %s",self.short_mac_name,hex(msg.cmd),print_hex(msg.payload))
                        _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                
                # unknown packet
                elif msg.cmd==0xfe:
                    self.short_mac=msg.payload[5:8]
                    self.short_mac_name="".join("%02x"%(n) for n in self.short_mac)
                    _LOGGER.warning("Plug ID: %s Received cmd 254 - propably something went wrong ", self.short_mac_name)
                    _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                else:
                    self.short_mac=msg.payload[5:8]
                    self.short_mac_name="".join("%02x"%(n) for n in self.short_mac)
                    _LOGGER.warning("Plug ID: %s Received unknown data with cmd id %s - %s", self.short_mac_name,msg.cmd,msg.payload)
                    _LOGGER.debug("Plug ID: %s CMD: %s Payload: %s", self.short_mac_name, hex(msg.cmd), print_hex(msg.payload))
                self.data = msg.next
            alive = time.time()
        return

class ThreadedEchoServer(socketserver.ThreadingMixIn,
                         socketserver.TCPServer,
    ):
    """ Register/bind server """
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
    #pass


if __name__ == "__main__":
    logging.basicConfig()
    if DEBUG:
        _LOGGER.setLevel(logging.DEBUG)
    else:
        _LOGGER.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.StreamHandler()
    log.setFormatter(formatter)
    _LOGGER.addHandler(log)
    _LOGGER.propagate=0



    HOST, PORT = "", 4196

    while True:
        try:
            server = ThreadedEchoServer((HOST, PORT),ThreadedEchoRequestHandler)
            _LOGGER.info("""*** starting params ***
                          MQTTHOST:%s
                          MQTTPORT:%d 
                          MQTTSSL:%s 
                          USERNAME:%s 
                          PASSWORD:**** 
                          RETAIN:%s 
                          AUTODISCOVERY:%s 
                          DISCOVERYTOPIC:%s
                          DEBUG:%s""",
                          MQTTHOST,MQTTPORT,MQTTSSL,USERNAME,RETAIN,AUTODISCOVERY,DISCOVERYTOPIC,DEBUG)
            _LOGGER.info("*** Server started! ***")
            break
        except Exception as srv_ex:
            _LOGGER.info("Port still busy...")
            _LOGGER.debug(srv_ex)
            time.sleep(1)
    
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
