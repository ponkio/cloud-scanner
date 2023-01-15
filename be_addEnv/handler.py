import logging
import boto3
from botocore.config import Config
import os 
import subprocess
import jinja2
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
    return req
