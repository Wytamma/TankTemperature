import os
import fnmatch
import time
import logging
from gmail import GMail, Message
from datetime import datetime
from _passwords import EMAIL_PASSWORD

logging.basicConfig(filename='/home/pi/DS18B20_error.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


gmail = GMail('TankTemp <wytamma@gmail.com>', EMAIL_PASSWORD)

def email(msgText, Email):
    """Sends msgText to Email"""
    msg = Message(
        msgText,
        to = '%s <%s>' % (Email),
        text = msgText
        )
    gmail.send(msg)


# Get readings from sensors and print
minTemp = 20
maxTemp = 28
lastEmailSent = 0
temperatures = []
IDs = []

while True:
    for filename in os.listdir("/sys/bus/w1/devices"):
        if not fnmatch.fnmatch(filename, '28-*'):
            continue
        with open("/sys/bus/w1/devices/" + filename + "/w1_slave") as f_obj:
            lines = f_obj.readlines()
            if lines[0].find("YES"):
                pok = lines[1].find('=')
                temperatures.append(float(lines[1][pok+1:pok+6])/1000)
                IDs.append(filename)
            else:
                logger.error("Error reading sensor with ID: %s" % (filename))

    if (len(temperatures) > 0):
        for i, temp in enumerate(temperatures):
            if temp > maxTemp or temp < minTemp:
                print("*"*50)
                print("WARNING: %s is outside the temperature range!!!" % IDs[i])
                print(IDs[i], temp)
                print("*"*50)
                # only send an email every 10mins
                if (time.time() - lastEmailSent) / 60 > 10:
                    email(
                        "WARNING: %s is outside the temperature range!!!\n\n\
                        Current temperature = %s˚C" % (IDs[i], temp),
                        "wytamma.wirth@me.com")
                    print("Email sent!")
                    lastEmailSent = time.time()

            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(now, IDs[i], temp)

    temperatures = []
    IDs = []
