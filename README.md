# TankTemperature
Automated water temperature monitoring system.

## Application cycle/idea
### RPi
- On start get list of probes attached to Rpi
- Tell server to create Tanks in tanks table using IDs
- Server will check if ID already exists else create a new tank entry
  - e.g. {'probe_id':probe_id, 'Name':null}
  - The Name key can be used for easy identification of each tank, however the probe_id is the main ID. This does lead to one obvious problem, the probe will have to remain in the same tank.  
- while True:
  - Recored temperature data in memory (enables some network interruption recovery)
  - When memory data reaches someSize send data to server (minimize requests)
  - If (temperature outside range): send alert


### client (React.js)
- On load request past 48hrs of data for each tank
- Make request to server for data every Min
  - Update sparkline


## TODO:
- Need to work out how much
