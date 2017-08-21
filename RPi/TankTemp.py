import os
import fnmatch
import time
from gmail import GMail, Message
from _passwords import EMAIL_PASSWORD, API_BASE_URL, WEB_APP_URL
import requests
import argparse
from datetime import datetime
import traceback
import logging
import sys

# Build argument parser, this allows you to parse comands from the cli
parser = argparse.ArgumentParser(description='Automated water temperature monitoring system.')
parser.add_argument('-i', '--interval', help='Sampling interval (mins)', type=float)
args = vars(parser.parse_args())

# Set up logging
logging.basicConfig(filename='TankTemp.log',level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Set up emailer
gmail = GMail('TankTemp <wytamma@gmail.com>', EMAIL_PASSWORD)


def email(msgSubject, msgText, Email):
    """Sends msgText to Email"""
    msg = Message(
        msgText,
        to='%s <%s>' % (Email, Email),
        text=msgText
        )
    gmail.send(msg)


print("Adding probes to database")
# add probe to DB if not in it already
probe_IDs = []
for filename in os.listdir("/sys/bus/w1/devices"):
    if not fnmatch.fnmatch(filename, '28-*'):
        continue
    probe_IDs.append(filename)

probes = [probe['probe_ID'] for probe in requests.get(API_BASE_URL + '/probes').json()['data']]

for probe_ID in probe_IDs:
    if probe_ID in probes:
        continue
    r = requests.post(
        API_BASE_URL + '/probes',
        data={'probe_ID': probe_ID}
        )
    print(r.json()['message'])

# default vars
samping_interval = args['interval'] or 10  # mins

records = []  # stores temperture records in memory before sending them to DB

while True:
    # get fresh probe info
    r = requests.get(API_BASE_URL + '/probes')
    if r.status_code == 200:
        probesInfoFromAPI = r.json()['data']
    else:
        probesInfoFromAPI = []


    # loop through all the probe datafiles
    for filename in os.listdir("/sys/bus/w1/devices"):
        record = {}

        # Only read files that match the probe ID format (all DS18B20 probes
        # start with '28-')
        if not fnmatch.fnmatch(filename, '28-*'):
            continue

        with open("/sys/bus/w1/devices/" + filename + "/w1_slave") as f_obj:
            # read data and check for probe errors
            lines = f_obj.readlines()
            if lines[0].find("YES") is -1:
                email(
                    "Error reading sensor with ID: %s" % (
                        filename), args['email']
                    )
            pok = lines[1].find('=')

            # Build record
            record['temperature'] = float(lines[1][pok+1:pok+6])/1000
            record['probe_ID'] = filename
            record['time'] = int(round(time.time() * 1000))  # milliseconds

            # Add record to list for later upload
            # this saves on the number of requests = $
            records.append(record)

            defaultInfo = {
                "probe_ID": record['probe_ID'],
                "name": None,
                "maxTemp": 28,
                "minTemp": 20,
                "alertSnooze": int(round(time.time() * 1000)),
                "whoToEmail": ['wytamma.wirth@me.com'],
                "default": True
                }

            # Find record info
            InfoFromAPI = next((probe for probe in probesInfoFromAPI if probe["probe_ID"] == record['probe_ID']), False)

            if InfoFromAPI is False:
                logger.error("Something broke...")
                logger.error(record)
                logger.error(probesInfoFromAPI)
                logger.error(traceback.format_exc())
                InfoFromAPI = defaultInfo

            # Update the console
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(now, record['probe_ID'], str(record['temperature'])+"˚C")

            t = record['temperature']
            maxTemp = InfoFromAPI['maxTemp']
            minTemp = InfoFromAPI['minTemp']

            if t < maxTemp and t > minTemp:
                # inside range
                continue

            # Warning
            msg = "WARNING: %s is outside the temperature range!!!" % record['probe_ID']
            msg2 = "Current temperature = %s˚C" % t
            print(msg)

            if int(round(time.time() * 1000)) < InfoFromAPI['alertSnooze']:
                print("Email snoozed")
                continue

            for Email in InfoFromAPI['whoToEmail']:
                print("Sending email to %s" % Email)
                try:
                    email(msg, msg+"\n"+msg2+"\n"+WEB_APP_URL+"\n"+str(InfoFromAPI), Email)
                    print("Email sent!")
                except:
                    logger.error("Email failed to send!")
                    logger.error(traceback.format_exc())

    # attempt insert
    try:
        json = {'data': records}
        r = requests.post(
            API_BASE_URL + '/temps', json=json)
        if r.status_code == 201:
            # records where successfully added
            # reset records store
            # If it fails don't reset so we can try again later
            records = []
        else:
            logger.error("Insert Failed")
            logger.error(traceback.format_exc())
            print(r.json()['message'])
    except:
        print("Request Failed")
    print("Sleeping for %s mins" % samping_interval)
    time.sleep(samping_interval*60)
