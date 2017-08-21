from flask import Flask
from pymongo import MongoClient
from flask_restful import Resource, reqparse, Api
from _passwords import MONGO_URI
from flask_cors import CORS
from time import time


app = Flask(__name__)
CORS(app)
api = Api(app)
app.config.from_object('config.BaseConfig')
client = MongoClient(MONGO_URI)
db = client.production


@app.route('/')
def index():
    return """Welcome to TankTemp, an automated water temperature
            monitoring system.""", 200


class Probelist(Resource):

    def add_probe(self, probe_ID):
        probe = {
            "probe_ID": probe_ID,
            "name": None,  # user friendly name of probe/tank
            "maxTemp": 28,  # default max temperture to alert at
            "minTemp": 20,  # default min temperture to alert at
            "whoToEmail": ['wytamma.wirth@me.com'],  # list of people to alert when limit reached
            "alertSnooze": int(round(time.time() * 1000)),  # time to wait until sending next alert
            }

        # search for probe_ID if not found: insert new
        object_id = db.tanks.update_one(
            {"probe_ID": probe_ID},
            {"$setOnInsert": probe},
            upsert=True
        )
        return object_id

    def update_probe(self, probe):
        # updates one probe doc if found
        object_id = db.tanks.update_one(
            {"probe_ID": probe['probe_ID']},
            {"$set": probe}
        )
        return object_id

    def get(self):
        return {"data": list(db.tanks.find({}, {'_id': False}))}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('probe_ID', required=True)

        args = parser.parse_args()
        result = self.add_probe(args['probe_ID'])
        if result.upserted_id:
            return {"message": "Probe %s added to database." % args['probe_ID']}, 201
        return {"message": "Probe %s already exists." % args['probe_ID']}, 400

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('probe_ID', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('maxTemp', required=True, type=int)
        parser.add_argument('minTemp', required=True, type=int)
        parser.add_argument('whoToEmail', required=True, type=list)
        parser.add_argument('alertSnooze', required=True, type=int)

        args = parser.parse_args()
        result = self.update_probe(args)
        if result.modified_count:
            return {"message": "Probe %s modified." % args['probe_ID']}, 200
        return {"message": "Probe %s not modified." % args['probe_ID']}, 400


class Temp(Resource):

    def get(self, probe_ID):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int)
        args = parser.parse_args()
        limit = args['limit'] or int((60*24)/10)  # 24 hours of records
        records = db.temps.find(
            {'probe_ID': probe_ID}, {'_id': False}
            ).sort([("_id", -1)]).limit(limit)

        return {"data": list(records)}, 200

    def put(self, probe_ID):
        """Add to probe"""
        parser = reqparse.RequestParser()
        parser.add_argument('probe_ID', required=True)
        parser.add_argument('temperature', required=True, type=float)
        parser.add_argument('time', required=True, type=int)

        args = parser.parse_args()

        result = db.temps.insert_one(args)
        if result.inserted_id:
            return {"message": "Added to probe %s." % probe_ID}, 201
        return {"message": "Failed to insert."}, 400



class Temps(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('data',
                        required=True,
                        action='append',
                        type=dict
                        )

    def post(self):
        """Add to probes from list"""
        args = self.parser.parse_args()
        results = db.temps.insert_many(args['data'])
        return {"message": "Added %s records." % len(results.inserted_ids)}, 201


api.add_resource(Probelist, '/probes')
api.add_resource(Temp, '/temps/<probe_ID>')
api.add_resource(Temps, '/temps')
