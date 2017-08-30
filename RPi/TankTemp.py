import os
import fnmatch
import time
from _passwords import API_BASE_URL, WEB_APP_URL
import requests
import argparse
from datetime import datetime
import traceback
import logging
import sys
from utils import email, mode_average
from tenacity import retry, stop_after_attempt, wait_fixed


# Build argument parser, this allows you to parse comands from the cli
parser = argparse.ArgumentParser(description='Automated water temperature monitoring system.')
parser.add_argument('-i', '--interval', help='Sampling interval (mins)', type=float)
args = vars(parser.parse_args())

# default vars
samping_interval = args['interval'] or 10  # mins

print("Starting...")

# Set up logging
logging.basicConfig(filename='TankTemp.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

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
    print("Adding probe %s to database" % probe_ID)
    r = requests.post(
        API_BASE_URL + '/probes',
        data={'probe_ID': probe_ID}
        )
    print(r.json()['message'])


@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def getTemperatureFromProbe(filename):
    """Get temperature data from probe."""
    logger.info("Getting data from %s" % filename)
    with open("/sys/bus/w1/devices/" + filename + "/w1_slave", 'r') as f_obj:
        # read data and check for probe errors
        lines = f_obj.readlines()
        if lines[0].find("YES") is -1:
            logger.error("Bad read. " + filename)
            logger.error(traceback.format_exc())
            raise IOError

        pok = lines[1].find('=')

        # Build record
        temperature = float(lines[1][pok+1:pok+6])/1000

        if temperature == 0:
            # retry instead
            logger.error("Bad read. " + record['probe_ID'])
            logger.error("Temperature == 0˚C")
            logger.error(traceback.format_exc())
            raise IOError

    return temperature


records = []  # stores temperture records in memory before sending them to DB

while True:
    # get fresh probe info
    try:
        r = requests.get(API_BASE_URL + '/probes')
        if r.status_code == 200:
            probesInfoFromAPI = r.json()['data']
        else:
            logger.error("r.status_code != 200")
            probesInfoFromAPI = []
    except requests.ConnectionError:
        logger.error("requests.ConnectionError")
        probesInfoFromAPI = []

    # loop through all the probe datafiles
    for probe in probesInfoFromAPI:
        filename = probe['probe_ID']
        record = {}
        # retry function ()
        # record = getRecord(filename)
        temperatures = []
        try:
            # build list of 3 samples to take datafrom
            for i in range(3):
                logger.info("Probe: %s Sample: %s" % (filename, i+1))
                # retry 5 times if fails to read
                # waiting 1s between each retry
                temperatures.append(getTemperatureFromProbe(filename))
        except:
            logger.error("Bad read. " + filename)
            logger.error("One sample failed 3 times")
            logger.error(traceback.format_exc())
            email("Error reading sensor",
                  "Error reading sensor with ID: %s \n %s" % (
                    filename, traceback.format_exc()),
                  'wytamma.wirth@me.com')

            continue

        if len(temperatures) != 3:
            logger.error("Bad sample. " + filename)
            logger.error("len(temperatures) != 3")
            continue

        record['temperature'] = mode_average(temperatures)
        record['probe_ID'] = filename
        record['time'] = int(round(time.time() * 1000))  # milliseconds


        # Add record to list for later upload
        # this saves on the number of requests = $$$
        records.append(record)

        InfoFromAPI = probe

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
        probe_name = InfoFromAPI['name'] or record['probe_ID']
        msg = "WARNING: %s is outside the temperature range!!!" % probe_name
        msg2 = "Current temperature = %s˚C" % t
        print(msg)

        if int(round(time.time() * 1000)) < InfoFromAPI['alertSnooze']:
            print("Email snoozed")
            continue

        for Email in InfoFromAPI['whoToEmail']:
            print("Sending email to %s" % Email)
            try:
                email(msg, msg+"\n"+msg2+"\n"+WEB_APP_URL, Email)
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
