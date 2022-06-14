#!/bin/bash

echo "Region $AWS_REGION"
echo "Queue $SQS_QUEUE_URL"
echo "Bucket $AWS_BUCKET"

# 1. CONFIGURE AWS CLI
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region $AWS_REGION
MY_INSTANCE_ID=$(curl http://169.254.169.254/latest/meta-data/instance-id)
echo "Instance ID $MY_INSTANCE_ID"
OWNER_ID=$(aws ec2 describe-instances --instance-ids $MY_INSTANCE_ID --output text --query 'Reservations[0].[OwnerId]')
aws ec2 create-tags --resources $MY_INSTANCE_ID --tags Key=Name,Value=${APP_NAME}Worker
VOL_0_ID=$(aws ec2 describe-instance-attribute --instance-id $MY_INSTANCE_ID --attribute blockDeviceMapping --output text --query BlockDeviceMappings[0].Ebs.[VolumeId])
aws ec2 create-tags --resources $VOL_0_ID --tags Key=Name,Value=${APP_NAME}Worker
VOL_1_ID=$(aws ec2 describe-instance-attribute --instance-id $MY_INSTANCE_ID --attribute blockDeviceMapping --output text --query BlockDeviceMappings[1].Ebs.[VolumeId])
aws ec2 create-tags --resources $VOL_1_ID --tags Key=Name,Value=${APP_NAME}Worker

# 2. SET UP ALARMS
aws cloudwatch put-metric-alarm --alarm-name ${APP_NAME}_${MY_INSTANCE_ID} --alarm-actions arn:aws:swf:${AWS_REGION}:${OWNER_ID}:action/actions/AWS_EC2.InstanceId.Terminate/1.0 --statistic Maximum --period 60 --threshold 1 --comparison-operator LessThanThreshold --metric-name CPUUtilization --namespace AWS/EC2 --evaluation-periods 15 --dimensions "Name=InstanceId,Value=${MY_INSTANCE_ID}"

# 3. RUN VM STAT MONITOR
python3.9 instance-monitor.py &

# 4. RUN CP WORKERS
python3.9 B2R-worker.py |& tee $k.out
