# Flask Server
Automated water temperature monitoring system API.

local
```
$ export FLASK_APP=hello.py
$ export FLASK_DEBUG=1
$ flask run
```

Production
```
$ zappa init
$ zappa deploy production
$ zappa update production
```

### API endpoints
/probes  
  GET - returns a list of probes  
  POST - adds probe to DB | requires: [probe_ID]  
  PUT - Updates probe info | requires: [probe_ID, name]  
/temps  
  POST - adds many temperature records at once  
/temps/<probe_ID>?limit=X  
  GET - returns X most recent records for probe_ID  
/temps/<probe_ID>  
  PUT - Adds record to specific probe_ID  
