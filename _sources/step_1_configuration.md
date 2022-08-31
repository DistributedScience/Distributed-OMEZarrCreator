# Step 1: Configuration

The first step in setting up any job is editing the values in the config.py file.
Once the config file is created, simply type `python run.py setup` to set up your resources based on the configurations you've specified.

***

## Components of the config file

* **APP_NAME:** This will be used to tie your clusters, tasks, services, logs, and alarms together.
It need not be unique, but it should be descriptive enough that you can tell jobs apart if you're running multiple jobs.
* **LOG_GROUP_NAME:** The name to give the log group that will monitor the progress of your jobs and allow you to check performance or look for problems after the fact.

***
### DOCKER REGISTRY INFORMATION

* **DOCKERHUB_TAG:** This is the encapsulated version of BioFormats2Raw you will be running.

***

### AWS GENERAL SETTINGS
These are settings that will allow your instances to be configured correctly and access the resources they need - see [Step 0: Prep](step_0_prep.md) for more information.

***

### EC2 AND ECS INFORMATION

* **ECS_CLUSTER:** Which ECS cluster you'd like the jobs to go into.
All AWS accounts come with a "default" cluster, but you may add more clusters if you like.
Distinct clusters for each job are not necessary, but if you're running multiple jobs at once it can help avoid the wrong Docker containers going to the wrong instances.
* **CLUSTER_MACHINES:** How many EC2 instances you want to have in your cluster.
* **TASKS_PER_MACHINE:** How many Docker containers to place on each machine.
* **MACHINE_TYPE:** A list of what type(s) of machines your spot fleet should contain.
* **MACHINE_PRICE:** How much you're willing to pay per hour for each machine launched.
AWS has a handy [price history tracker](https://console.aws.amazon.com/ec2sp/v1/spot/home) you can use to make a reasonable estimate of how much to bid.
If your jobs complete quickly and/or you don't need the data immediately you can reduce your bid accordingly; jobs that may take many hours to finish or that you need results from immediately may justify a higher bid.
* **EBS_VOL_SIZE:** The size of the temporary hard drive associated with each EC2 instance in GB.
The minimum allowed is 22.
If you have multiple Dockers running per machine, each Docker will have access to (EBS_VOL_SIZE/TASKS_PER_MACHINE) - 2 GB of space.

***

### DOCKER INSTANCE RUNNING ENVIRONMENT
* **CPU_SHARES:** How many CPUs each Docker container may have. (1024 units = 1 core)
* **MEMORY:** How much memory each Docker container may have.

***

### SQS QUEUE INFORMATION

* **SQS_QUEUE_NAME:** The name of the queue where all of your jobs will be sent.
* **SQS_MESSAGE_VISIBILITY:** How long each job is hidden from view before being allowed to be tried again.
We recommend setting this to slightly longer than the average amount of time it takes an individual job to process - if you set it too short, you may waste resources doing the same job multiple times; if you set it too long, your instances may have to wait around a long while to access a job that was sent to an instance that stalled or has since been terminated.
See [SQS_QUEUE_information](SQS_QUEUE_information) for more information.
* **SQS_DEAD_LETTER_QUEUE:** The name of the queue to send jobs to if they fail to process correctly multiple times.
This keeps a single bad job (such as one where a single file has been corrupted) from keeping your cluster active indefinitely.
See [Step 0: Prep](step_0_prep.med) for more information.

***

### REDUNDANCY CHECKS

* **CHECK_IF_DONE_BOOL:** Whether or not to check the output folder before proceeding.
Case-insensitive.
If an analysis fails partway through (due to some of the files being in the wrong place, an AWS outage, a machine crash, etc.), setting this to 'True' this allows you to resubmit the whole analysis but only reprocess jobs that haven't already been done.
This saves you from having to try to parse exactly which jobs succeeded versus failed or from having to pay to rerun the entire analysis.
If Distributed-OMEZARRCreator determines the correct number of files are already in the output folder it will designate that job as completed and move onto the next one.
If you actually do want to overwrite files that were previously generated (such as when you have improved a pipeline and no longer want the output of the old version), set this to 'False' to process jobs whether or not there are already files in the output folder.
