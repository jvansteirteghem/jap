from twisted.application import internet, service
import os
import logging
import JAP.JAP_LOCAL
import JAP.JAP_REMOTE_WS

configuration = JAP.JAP_LOCAL.getConfiguration("./JAP_REMOTE_WS.json", JAP.JAP_REMOTE_WS.getDefaultConfiguration)

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
    factory = JAP.JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "wss://" + str(os.environ["OPENSHIFT_DIY_IP"]) + ":" + str(os.environ["OPENSHIFT_DIY_PORT"]), debug = False)
    factory.protocol = JAP.JAP_REMOTE_WS.WSInputProtocol
else:
    factory = JAP.JAP_REMOTE_WS.WSInputProtocolFactory(configuration, "ws://" + str(os.environ["OPENSHIFT_DIY_IP"]) + ":" + str(os.environ["OPENSHIFT_DIY_PORT"]), debug = False)
    factory.protocol = JAP.JAP_REMOTE_WS.WSInputProtocol

application = service.Application("JAP")

server = internet.TCPServer(int(os.environ["OPENSHIFT_DIY_PORT"]), factory, interface=str(os.environ["OPENSHIFT_DIY_IP"]))
server.setServiceParent(application)
