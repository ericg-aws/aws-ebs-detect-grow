import boto3
import time

def lambda_handler(event, context):
    print(event)
    instance_id = event['ec2_instance_id']
    mountpoint = event['ec2_mountpoint']
    region = 'us-east-1'

    ssm = boto3.client('ssm', region_name=region)
    print(instance_id, mountpoint)
    try:
        print(f'Sending SSM document mountpoint parameter of: {mountpoint}')
        response = ssm.send_command(InstanceIds=[instance_id],
                                    DocumentName='ec2-expand-fs-linux',
                                    Parameters={"mountpoint": [mountpoint]}
                                    )
        command_id = response.get('Command', {}).get("CommandId", None)
        time.sleep(10)
        while True:
            # wait for SSM reponse 
            response = ssm.list_command_invocations(CommandId=command_id, Details=True)
            # if the command has not started to run yet, keep waiting
            if len(response['CommandInvocations']) == 0:
                time.sleep(1)
                continue
            invocation = response['CommandInvocations'][0]
            if invocation['Status'] not in ('Pending', 'InProgress', 'Cancelling'):
                break
            time.sleep(3)
        command_plugin = invocation['CommandPlugins'][-1]
        output = command_plugin['Output']
        return_string = output.strip()
        return {'status': return_string}
    except Exception as e: 
        print(e)
        print(f'An error occurred during invocation of the ssm document - ec2-expand-fs-linux')
        return {'status': 'error', 'message': e}