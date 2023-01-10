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

def aws_session(role_arn=None, session_name=None, external_id=None):
    """
    If role_arn is given assumes a role and returns boto3 session
    otherwise return a regular session with the current IAM user/role
    """
    if role_arn:
        client = boto3.client('sts')
        response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name, ExternalId=external_id)
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'])

        os.environ['AWS_ACCESS_KEY_ID'] = response['Credentials']['AccessKeyId']
        os.environ['AWS_SECRET_ACCESS_KEY'] = response['Credentials']['SecretAccessKey']
        os.environ['AWS_SESSION_TOKEN'] = response['Credentials']['SessionToken']
        
        return session
    else:
        return boto3.Session()

def patch_sp_config(sp_config):
    with open('./function/templates/aws.spc.j2','r') as file_:
        template = jinja2.Template(file_.read())
    
    with open('/home/app/.steampipe/config/aws.spc', 'w') as config:
        config.write(template.render(sp_config))

def handle(req):
    """handle a request to the function
    Args:
        req (Obj): {request body}
        Schema:
        {
            "customer":"tenant1"
        }
    """

    
    ## Get customer configuration
    logging.debug("Getting customer steampipe configruation")
    customer_session = aws_session(role_arn='arn:aws:iam::756114516798:role/landscape_monitoring_dev', session_name='SSP-Session', external_id='securesea')
    sp_config = {
        "sp_regions": '["us-east-1"]'
    }
    patch_sp_config(sp_config)


    sp_query = "select * from aws_ec2_instance"    
    cmd = f"steampipe query '{sp_query}' --output json"

    logging.debug(f"Executing steampipe query: {sp_query}")    
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    
    
    ## This is where the "Cloud Sync" UI component will get its error from i.e the api return
    if stderr:
        logging.error(f"Steampipe query encountered an error: {stderr}")
        return stderr
    else:
        res = json.loads(stdout.decode('utf-8'))
        logging.debug(f"Returning {len(res)}")
        return res

    # ec2_client = customer_session.client('ec2', config = boto_config)

    # ec2_list = ec2_client.describe_instances()

    logging.debug(ec2_list)
    # ssp_user_list = {}
    # for user in user_list['Users']:
    #     access_keys = iam_client.list_access_keys(UserName=user.UserName)
        
    logging.debug(customer_session)
    return req
