# Constants (User configurable)

APP_NAME = 'DistributedBioFormats2Raw'                # Used to generate derivative names unique to the application.

# DOCKER REGISTRY INFORMATION:
DOCKERHUB_TAG = 'openmicroscopy/bioformats2raw:0.4.0'

# AWS GENERAL SETTINGS:
AWS_REGION = 'us-east-1'
AWS_PROFILE = 'default'                 # The same profile used by your AWS CLI installation
SSH_KEY_NAME = 'your-key-file.pem'      # Expected to be in ~/.ssh
AWS_BUCKET = 'your-bucket-name'

# EC2 AND ECS INFORMATION:
ECS_CLUSTER = 'default'
CLUSTER_MACHINES = 3
TASKS_PER_MACHINE = 1
MACHINE_TYPE = ['m4.xlarge']
MACHINE_PRICE = 0.10
EBS_VOL_SIZE = 30                       # In GB.  Minimum allowed is 22.

# DOCKER INSTANCE RUNNING ENVIRONMENT:
DOCKER_CORES = 4                        # Number of BioFormats2Raw processes to run inside a docker container
CPU_SHARES = DOCKER_CORES * 1024        # ECS computing units assigned to each docker container (1024 units = 1 core)
MEMORY = 15000                           # Memory assigned to the docker container in MB
SECONDS_TO_START = 3*60                 # Wait before the next process is initiated to avoid memory collisions

# SQS QUEUE INFORMATION:
SQS_QUEUE_NAME = APP_NAME + 'Queue'
SQS_MESSAGE_VISIBILITY = 1*60           # Timeout (secs) for messages in flight (average time to be processed)
SQS_DEAD_LETTER_QUEUE = 'arn:aws:sqs:some-region:111111100000:DeadMessages'

# LOG GROUP INFORMATION:
LOG_GROUP_NAME = APP_NAME

# REDUNDANCY CHECKS
CHECK_IF_DONE_BOOL = 'False'  #True or False- should it check if there are a certain number of non-empty files and delete the job if yes?

# PUT ANYTHING SPECIFIC TO YOUR PROGRAM DOWN HERE
