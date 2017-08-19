from flask import Flask
from pymongo import MongoClient
from flask_restful import Resource, reqparse, Api
from _passwords import MONGO_URI

app = Flask(__name__)
api = Api(app)


app.config.from_object('config.BaseConfig')
client = MongoClient(MONGO_URI)
db = client.test


@app.route('/')
def index():
    return "Chralie is gay and writes for the wrong side.", 200


class Probelist(Resource):

    def add_probe(self, probe_ID):
        probe = {"probe_ID": probe_ID,
                 "name": None,
                 }

        # search for probe_ID if not
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
            return {"message": "Probe Added"}, 201
        return {"message": "Probe %s already exists" % args['probe_ID']}, 400

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('probe_ID', required=True)
        parser.add_argument('name', required=True)

        args = parser.parse_args()
        result = self.update_probe(args)
        if result.modified_count:
            return {"message": "Probe modified"}, 200
        return {"message": "Probe not modified"}, 400


class Temp(Resource):

    def get(self, probe_ID):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int)
        args = parser.parse_args()
        limit = args['limit'] or int((60*48)/10) # 10 mins in a day
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
            return {"message": "Added to probe %s" % probe_ID}, 201
        return {"message": "Failed to insert"}, 400



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
        print(args['data'])
        results = db.temps.insert_many(args['data'])
        return "Added %s records" % len(results.inserted_ids), 201


api.add_resource(Probelist, '/probes')
api.add_resource(Temp, '/temps/<probe_ID>')
api.add_resource(Temps, '/temps')