import boto3 
import re

def lambda_handler(event, context):
    print(event)
    ebs_id_string = event['ec2_ebs_string']
    region = 'us-east-1'

    try:
        ec2_resource = boto3.resource('ec2', region_name=region)
        result = re.search("(vol.*)", ebs_id_string)
        vol_id = result.group(1)
        vol = ec2_resource.Volume(vol_id)
        vol_new_size = int((vol.size*1.01))

        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.create_snapshot(
            Description="Created by step function - ec2-fs-expand",
            VolumeId=vol_id,
            DryRun=False
        )
        # response is a dictionary containing ResponseMetadata and SnapshotId
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        snapshot_id = response['SnapshotId']
        # check if the snapshot was created successfully then proceed to grow
        if status_code == 200:
            print(f"Snapshot successful for volume ID: {vol_id}")
            print(f"Growing volume ID: {vol_id} from {vol.size} to {vol_new_size} ")
            response = ec2_client.modify_volume(
                VolumeId=vol_id,
                Size=vol_new_size
            )
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            if status_code == 200:
                print(f"Volume ID: {vol_id}, grown from {vol.size} to {vol_new_size}")
            return {'status': 'success', 'ec2_mountpoint': event['ec2_mountpoint'], 'ec2_instance_id': event['ec2_instance_id']}
        else:
            raise Exception('Snapshot process not validated')
    except Exception as e: 
        print(e)
        print(f"An error occurred during the EBS snapshot or grow steps - volume ID: {vol_id}")
        return {'status': 'error', 'message': e}
