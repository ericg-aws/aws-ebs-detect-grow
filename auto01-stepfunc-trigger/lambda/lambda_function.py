import boto3 
from datetime import datetime
import os 
import json

def lambda_handler(event, context):
    state_machine_arn = os.environ['state_machine_arn']
    ec2_mountpoint = event['detail']['configuration']['metrics'][0]['metricStat']['metric']['dimensions']['path']
    ec2_instance_id = event['detail']['configuration']['metrics'][0]['metricStat']['metric']['dimensions']['InstanceId']
    ec2_fstype = event['detail']['configuration']['metrics'][0]['metricStat']['metric']['dimensions']['fstype']
    ec2_os = 'al2'

    try:
        datetime_current = datetime.now()
        step_execution_name = datetime_current.strftime("%G%B%dHour%HMin%MSec%S")
        
        print(event)
        print(state_machine_arn, ec2_mountpoint, ec2_instance_id, ec2_fstype)
        
        json_string = {
            "state_machine_arn": state_machine_arn,
            "ec2_fstype":ec2_fstype,
            "ec2_instance_id": ec2_instance_id,
            "ec2_mountpoint": ec2_mountpoint,
            "ec2_os": ec2_os
        }
        json_object = json.dumps(json_string)

        sf = boto3.client('stepfunctions')    
        
        sf.start_execution(    
            stateMachineArn=state_machine_arn,    
            name=step_execution_name,    
            input=json_object
        )   
    except Exception as e: 
        print(e)
        print("An error occurred during state machine execution or prep")
        return {'status': 'error', 'message': e}