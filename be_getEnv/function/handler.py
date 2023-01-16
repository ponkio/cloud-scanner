import logging
import pymongo
import os
import json

logging.basicConfig(
    filename="aws-scanner.log",
    level=logging.DEBUG,
    format= '%(created)f:%(levelname)s:%(name)s:%(module)s:%(message)s'
)


def handle(req):
    """handle a request to the function
    Args:
        req (Obj): {request body}
        Schema:
        {
            "customer":"tenant1"
        }
    """

    with open("/var/openfaas/secrets/root-pwd", "r") as pwd_file:
        mongo_url = f"mongodb://root:{pwd_file.read()}@mongo-mongodb.mongo:27017/"
    
    logging.debug(f"Attempting connection to: {mongo_url.split('@')[1]}")

    mongoClient = pymongo.MongoClient(mongo_url)

    customer_id = os.environ['Http_Customerid']
    db = mongoClient[customer_id]
    
    config_collection = db['landscape_config']


    try:
        logging.info(f"Getting environments for {customer_id}")
        return_list = config_collection.find()
        return json.dumps({"status":200,"message":return_list})
    except Exception as err:
        return json.dumps({"status":500, "message": err})
    