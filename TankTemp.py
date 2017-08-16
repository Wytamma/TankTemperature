import os
import fnmatch
import time
import logging
from gmail import GMail, Message


logging.basicConfig(filename='/home/pi/DS18B20_error.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

lastEmailSent = 0
gmail = GMail('TankTemp <wytamma@gmail.com>','cQ3-GgP-Pdk-GPZ')


def email(msgText):
    global lastEmailSent
    if (time.time() - lastEmailSent) / 60 > 5:
        msg = Message(
            msgText,
            to = '%s <%s>' % ("Wytamma", "wytamma.wirth@me.com"),
            text = msgText
            )
        gmail.send(msg)
        lastEmailSent = time.time()
        return True
    else:
        return False

# Get readings from sensors and print
minTemp = 20
maxTemp = 28
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

    if (len(temperatures)>0):
        for i, temp in enumerate(temperatures):
            if temp > maxTemp or temp < minTemp:
                print("*"*50)
                print("WARNING: %s is outside the temperature range!!!" % IDs[i])
                print(IDs[i], temp)
                print("*"*50)
                if email("WARNING: %s is outside the temperature range!!!\n\nCurrent temperature = %s˚C" % (IDs[i], temp)):
                    print("Email sent!")
            else:
                print(IDs[i], temp)
    temperatures = []
    IDs = []
