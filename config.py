# Constants (User configurable)

APP_NAME = 'DistributedBioFormats2Raw'                # Used to generate derivative names unique to the application.
LOG_GROUP_NAME = APP_NAME

# DOCKER REGISTRY INFORMATION:
DOCKERHUB_TAG = 'erinweisbart/distributed-bioformats2raw:0.0.19'

# AWS GENERAL SETTINGS:
AWS_REGION = 'us-east-1'
AWS_PROFILE = 'default'                 # The same profile used by your AWS CLI installation
SSH_KEY_NAME = 'your-key-file.pem'      # Expected to be in ~/.ssh
AWS_BUCKET = 'your-bucket-name'         # Bucket to use for logging

# EC2 AND ECS INFORMATION:
ECS_CLUSTER = 'default'
CLUSTER_MACHINES = 1                    # Set to <= number of plates you have to process
TASKS_PER_MACHINE = 1
MACHINE_TYPE = ['c5.xlarge']
MACHINE_PRICE = 0.10
EBS_VOL_SIZE = 300                      # In GB.  Make large enough for your source images + .ome.zarr

# DOCKER INSTANCE RUNNING ENVIRONMENT:
CPU_SHARES = 1024        # ECS computing units assigned to each docker container (1024 units = 1 core)
MEMORY = 7500                           # Memory assigned to the docker container in MB

# SQS QUEUE INFORMATION:
SQS_QUEUE_NAME = APP_NAME + 'Queue'
SQS_MESSAGE_VISIBILITY = 4*60*60        # Timeout (secs) for messages in flight (average time to be processed)
SQS_DEAD_LETTER_QUEUE = 'arn:aws:sqs:some-region:111111100000:DeadMessages'

# REDUNDANCY CHECKS
CHECK_IF_DONE_BOOL = 'False'  #True or False - should it check if there is already a .zarr file and delete the job if yes?
