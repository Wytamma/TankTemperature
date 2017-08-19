import os
import fnmatch
import time
from gmail import GMail, Message
from _passwords import EMAIL_PASSWORD, API_BASE_URL
import requests
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(
    description='Automated water temperature monitoring system.')
parser.add_argument(
    '-i', '--interval', help='Sampling interval (mins)')
parser.add_argument(
    '-M', '--max', help='Maximum temperature before warning', required=True)
parser.add_argument(
    '-m', '--min', help='Minimum temperature before warning', required=True)
parser.add_argument(


            
    '-e', '--email', help='Who to Email', required=True)

args = vars(parser.parse_args())
gmail = GMail('TankTemp <wytamma@gmail.com>', EMAIL_PASSWORD)

def email(msgText, Email):
    """Sends msgText to Email"""
    msg = Message(
        msgText,
        to='%s <%s>' % (Email),
        text=msgText
        )
    gmail.send(msg)\

# get all probes
probe_IDs = []

for filename in os.listdir("/sys/bus/w1/devices"):
    if not fnmatch.fnmatch(filename, '28-*'):
        continue
    probe_IDs.append(filename)

probes = requests.get(API_BASE_URL + '/probes').json()['data']

# add probe to DB if not in it already
for probe_ID in probe_IDs:
    if probe_ID in probes:
        continue
    r = requests.post(
        API_BASE_URL + '/probes',
        data={'probe_ID': probe_ID}
        )
    print(r.json()['message'])

# Vars
minTemp = args['max']
maxTemp = args['min']
records = []
samping_interval = args['interval'] or 10  # mins

while True:
    for filename in os.listdir("/sys/bus/w1/devices"):
        record = {}
        if not fnmatch.fnmatch(filename, '28-*'):
            continue

        with open("/sys/bus/w1/devices/" + filename + "/w1_slave") as f_obj:
            lines = f_obj.readlines()
            if lines[0].find("YES"):
                pok = lines[1].find('=')
                record['temperature'] = float(lines[1][pok+1:pok+6])/1000
                record['probe_ID'] = filename
                record['time'] = int(round(time.time() * 1000))
                records.append(record)

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(now, record['probe_ID'], str(record['temperature'])+"˚C")

                t = record['temperature']
                if t > maxTemp or t < minTemp:
                    msg = "WARNING: %s is outside the temperature range!!!\n\n\
                    Current temperature = %s˚C" % (
                        record['probe_ID'],
                        record['temperature']
                        )
                    print(msg)
                    try:
                        email(msg, args['email'])
                        print("Email sent!")
                    except:
                        print("Email failed to send!")

            else:
                print("Error reading sensor with ID: %s" % (filename))

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
            print("Insert Failed")
            print(r.json()['message'])
    except:
        print("Request Failed")

    time.sleep(samping_interval*60)
