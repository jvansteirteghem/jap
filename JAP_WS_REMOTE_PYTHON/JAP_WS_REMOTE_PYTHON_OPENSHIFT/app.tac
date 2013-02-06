from twisted.application import internet, service
import json
import os
import logging
import JAP.JAP_WS_REMOTE

configuration = json.load(open("JAP_WS_REMOTE.json"))

JAP.JAP_WS_REMOTE.setDefaultConfiguration(configuration)

logging.basicConfig(filename=str(os.environ["OPENSHIFT_DIY_LOG_DIR"]) + "/jap.log")
logger = logging.getLogger("JAP")

if configuration["LOGGER"]["LEVEL"] == "DEBUG":
    logger.setLevel(logging.DEBUG)
else:
    if configuration["LOGGER"]["LEVEL"] == "INFO":
        logger.setLevel(logging.INFO)
    else:
        if configuration["LOGGER"]["LEVEL"] == "WARNING":
            logger.setLevel(logging.WARNING)
        else:
            if configuration["LOGGER"]["LEVEL"] == "ERROR":
                logger.setLevel(logging.ERROR)
            else:
                if configuration["LOGGER"]["LEVEL"] == "CRITICAL":
                    logger.setLevel(logging.CRITICAL)
                else:
                    logger.setLevel(logging.NOTSET)

if configuration["REMOTE_PROXY_SERVER"]["TYPE"] == "HTTPS":
    factory = JAP.JAP_WS_REMOTE.WSInputProtocolFactory(configuration, "wss://" + str(os.environ["OPENSHIFT_INTERNAL_IP"]) + ":" + str(os.environ["OPENSHIFT_INTERNAL_PORT"]), debug = False)
    factory.protocol = JAP.JAP_WS_REMOTE.WSInputProtocol
else:
    factory = JAP.JAP_WS_REMOTE.WSInputProtocolFactory(configuration, "ws://" + str(os.environ["OPENSHIFT_INTERNAL_IP"]) + ":" + str(os.environ["OPENSHIFT_INTERNAL_PORT"]), debug = False)
    factory.protocol = JAP.JAP_WS_REMOTE.WSInputProtocol

application = service.Application("JAP")

server = internet.TCPServer(int(os.environ["OPENSHIFT_INTERNAL_PORT"]), factory, interface=str(os.environ["OPENSHIFT_INTERNAL_IP"]))
server.setServiceParent(application)
