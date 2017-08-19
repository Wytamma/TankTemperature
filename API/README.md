# Flask Server
Automated water temperature monitoring system.

*Unless you need server side rendering for something, I create a separate app with create-react-app and build static assets from that, deploy to s3/cloudfront, and have it talk to my flask app which is API only. Nice separation of concerns, hosting the front end is insanely cheap and stable, and it avoids screwing around with webpack and mashing together JS and Python stuff.*

```
$ export FLASK_APP=hello.py
$ export FLASK_DEBUG=1
$ flask run
```
