import logging
import pymongo
import os
import json

logging.basicConfig(
    filename="be_AddEnv.log",
    level=logging.DEBUG,
    format= '%(created)f:%(levelname)s:%(name)s:%(module)s:%(message)s'
)

def strToCron(schedule):

    if schedule == "hourly":
        cronStr = "0 * * * *"
    elif schedule == "daily":
        cronStr = "0 0 * * *"
    elif schedule == "weekly":
        cronStr = "0 0 * * 5"
    else:
        return None
    return cronStr

def cloudIcon(cloud):

    if cloud == "aws":
        obj = { "name" : "aws", "icon": "https://img.icons8.com/material/96/FF9900/amazon-web-services.png" }
    elif cloud == "gcp":
        obj = { "name" : "gcp", "icon": "https://img.icons8.com/color/96/null/google-cloud.png" }

    return obj

def handle(req):
    """handle a request to the function
    Args:
        req (Obj): {request body}
        Schema:
        {
            "name": String,
            "cloud": String,
            "auth": Object,
            "schedule": String
        }
    """
    with open("/var/openfaas/secrets/root-pwd", "r") as pwd_file:
        mongo_url = f"mongodb://root:{pwd_file.read()}@mongo-mongodb.mongo:27017/"
    
    logging.debug(f"Attempting connection to: {mongo_url.split('@')[1]}")

    mongoClient = pymongo.MongoClient(mongo_url)


    customer_id = os.environ['Http_Customerid']
    req = json.loads(req)

    req['schedule'] = strToCron(req['schedule'])
    req['cloud'] = cloudIcon(req['cloud'])
    req['env_id'] = req['auth']['role_arn'].split(":")[4]


    logging.info(f"Adding entry for new environment: {customer_id}/{req['name']}")

    db = mongoClient[customer_id]

    config_collection = db['landscape_config']

    try:
        config_collection.insert_one(req)
        logging.debug("Configuration entry added")
        return json.dumps({ "status": 200, "message": "Configuration added"})
    except Exception as err:
        logging.error(f"Unable to add configuration entry: {err}")
        return json.dumps({ "status": 500, "message": str(err)})
