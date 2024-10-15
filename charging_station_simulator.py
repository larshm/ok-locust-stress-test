
import time
import uuid
import json
import ssl
import base64
import websocket
from locust import task
from locust_plugins.users.socketio import SocketIOUser

ChargingStations = []

class ChargingStationFlowTest(SocketIOUser):

    def __init__(self, parent):
        super().__init__(parent)
        self.chargingStation = ChargingStations.pop()

    @task
    def charging_station_connect(self):
        self.MessageResponses = {}
        self.MessageRequests = {}
        
        print("Connect to websocket")
        
        authUsername = bytes(self.chargingStation + ":", "utf-8")
        authPassword = bytes.fromhex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
        authString = base64.b64encode(authUsername + authPassword).decode("utf-8")

        #self.connect("wss://iris-emobility.test.okcloud.dk/ws/00400", [], subprotocols=["ocpp1.6"], sslopt={"cert_reqs": ssl.CERT_NONE})
        #self.connect(f"wss://host.docker.internal:6003/ws/{self.chargingStation}", [], subprotocols=["ocpp1.6"], sslopt={"cert_reqs": ssl.CERT_NONE})
        self.connect(f"wss://localhost:6003/ws/{self.chargingStation}", ["Authorization: Basic " + authString], subprotocols=["ocpp1.6"], sslopt={"cert_reqs": ssl.CERT_NONE})
        #self.connect(f"wss://localhost:6003/ws/LARSTEST", [], subprotocols=["ocpp1.6"])

        print("send boot notification request")
        bootNotificationConf = self.sendBootNotification()

        print("receive get configuration request")
        getConfigurationConf = self.receiveGetConfiguration()
        
        # sleep while sending heartbeats
        #self.sleep_with_heartbeat(10)
        self.closeConnection()

    def sendBootNotification(self):
        bootNotificationMessageId = str(uuid.uuid4())
        reqJson = f'[2,"{bootNotificationMessageId}","BootNotification",{{"chargePointVendor": "Domo", "chargePointModel": "Testmodel", "firmwareVersion": "1.5.4", "meterSerialNumber": "SimulatedMeter"}}]'
        #self.ws.send(reqJson, websocket.ABNF.OPCODE_TEXT)
        self.send(reqJson, "send BootNotification")

        while bootNotificationMessageId not in self.MessageResponses:
            time.sleep(0.1)
        
        bootNotificationConf = self.MessageResponses.pop(bootNotificationMessageId)

        print("Boot notification result: " + bootNotificationConf[2]["status"])

        return bootNotificationConf

    def receiveGetConfiguration(self):
        while "GetConfiguration" not in self.MessageRequests:
            time.sleep(0.1)
        
        getConfigurationReq = self.MessageRequests.pop("GetConfiguration")

        confJson = f'[3,"{getConfigurationReq[1]}",{{ "configurationKey": [], "unknownKey": null }}]'
        self.send(confJson, "receive GetConfiguration")
        #self.ws.send(confJson, websocket.ABNF.OPCODE_TEXT)

        return json.loads(confJson)
    
    def on_message(self, message):
        messageJson = json.loads(message)

        if messageJson[0] == 2: # request
            self.MessageRequests[messageJson[2]] = messageJson
        elif messageJson[0] == 3: # response
            self.MessageResponses[messageJson[1]] = messageJson
    
    def closeConnection(self, context = {}):
        self.environment.events.request.fire(
            request_type="WSS",
            name="Close websocket connection",
            response_time=None,
            response_length=0,
            exception=None,
            context={**self.context(), **context},
        )

        self.ws.close(websocket.STATUS_NORMAL)