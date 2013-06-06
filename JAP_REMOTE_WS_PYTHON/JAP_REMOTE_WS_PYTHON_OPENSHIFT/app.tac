from twisted.application import internet, service
import os
import logging
import JAP.REMOTE_WS.JAP_LOCAL
import JAP.REMOTE_WS.JAP_REMOTE_WS

file = open("./JAP_REMOTE_WS.json", "r")
data = file.read()
file.close()

configuration = JAP.REMOTE_WS.JAP_LOCAL.decodeJSON(data)
JAP.REMOTE_WS.JAP_REMOTE_WS.setDefaultConfiguration(configuration)

logging.basicConfig(filename=str(os.environ["OPENSHIFT_DIY_LOG_DIR"]) + "/jap.log")
logger = logging.getLogger("JAP.REMOTE_WS")

if configuration["LOGGER"]["LEVEL"] == "DEBUG":
    logger.setLevel(logging.DEBUG)
elif configuration["LOGGER"]["LEVEL"] == "INFO":
    logger.setLevel(logging.INFO)
elif configuration["LOGGER"]["LEVEL"] == "WARNING":
    logger.setLevel(logging.WARNING)
elif configuration["LOGGER"]["LEVEL"] == "ERROR":
    logger.setLevel(logging.ERROR)
elif configuration["LOGGER"]["LEVEL"] == "CRITICAL":
    logger.setLevel(logging.CRITICAL)
else:
    logger.setLevel(logging.NOTSET)

if configuration["REMOTE_PROXY_SERVER"]["TYPE"] == "HTTPS":
    factory = JAP.REMOTE_WS.JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "wss://" + str(os.environ["OPENSHIFT_INTERNAL_IP"]) + ":" + str(os.environ["OPENSHIFT_INTERNAL_PORT"]), debug = False)
    factory.protocol = JAP.REMOTE_WS.JAP_REMOTE_WS.WSInputProtocol
else:
    factory = JAP.REMOTE_WS.JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "ws://" + str(os.environ["OPENSHIFT_INTERNAL_IP"]) + ":" + str(os.environ["OPENSHIFT_INTERNAL_PORT"]), debug = False)
    factory.protocol = JAP.REMOTE_WS.JAP_REMOTE_WS.WSInputProtocol

application = service.Application("JAP")

server = internet.TCPServer(int(os.environ["OPENSHIFT_INTERNAL_PORT"]), factory, interface=str(os.environ["OPENSHIFT_INTERNAL_IP"]))
server.setServiceParent(application)
