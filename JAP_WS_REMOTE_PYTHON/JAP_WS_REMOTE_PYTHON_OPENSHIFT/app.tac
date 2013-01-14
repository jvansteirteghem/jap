from twisted.application import internet, service
import json
import os
import logging
import JAP.JAP_WS_REMOTE

configuration = json.load(open("JAP_WS_REMOTE.json"))

JAP.JAP_WS_REMOTE.setDefaultConfiguration(configuration)

logging.basicConfig(filename=str(os.environ["OPENSHIFT_DIY_LOG_DIR"]) + "/jap.log")
logger = logging.getLogger("JAP")
logger.setLevel(configuration["LOGGER"]["LEVEL"])

if configuration["REMOTE_PROXY_SERVER"]["TYPE"] == "HTTPS":
    factory = JAP.JAP_WS_REMOTE.WSInputProtocolFactory(configuration, "wss://" + str(os.environ["OPENSHIFT_INTERNAL_IP"]) + ":" + str(os.environ["OPENSHIFT_INTERNAL_PORT"]), debug = False)
    factory.protocol = JAP.JAP_WS_REMOTE.WSInputProtocol
else:
    factory = JAP.JAP_WS_REMOTE.WSInputProtocolFactory(configuration, "ws://" + str(os.environ["OPENSHIFT_INTERNAL_IP"]) + ":" + str(os.environ["OPENSHIFT_INTERNAL_PORT"]), debug = False)
    factory.protocol = JAP.JAP_WS_REMOTE.WSInputProtocol

application = service.Application("JAP")

server = internet.TCPServer(int(os.environ["OPENSHIFT_INTERNAL_PORT"]), factory, interface=str(os.environ["OPENSHIFT_INTERNAL_IP"]))
server.setServiceParent(application)
