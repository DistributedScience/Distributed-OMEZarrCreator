import boto3
import json
import logging
import os
import subprocess
import time
import watchtower

#################################
# CONSTANT PATHS IN THE CONTAINER
#################################

QUEUE_URL = os.environ["SQS_QUEUE_URL"]
LOG_GROUP_NAME = os.environ["LOG_GROUP_NAME"]
if "CHECK_IF_DONE_BOOL" not in os.environ:
    CHECK_IF_DONE_BOOL = False
else:
    CHECK_IF_DONE_BOOL = os.environ["CHECK_IF_DONE_BOOL"]
if "MIN_FILE_SIZE_BYTES" not in os.environ:
    MIN_FILE_SIZE_BYTES = 1
else:
    MIN_FILE_SIZE_BYTES = int(os.environ["MIN_FILE_SIZE_BYTES"])
if "USE_PLUGINS" not in os.environ:
    USE_PLUGINS = "False"
else:
    USE_PLUGINS = os.environ["USE_PLUGINS"]
if "NECESSARY_STRING" not in os.environ:
    NECESSARY_STRING = False
else:
    NECESSARY_STRING = os.environ["NECESSARY_STRING"]
if "DOWNLOAD_FILES" not in os.environ:
    DOWNLOAD_FILES = False
else:
    DOWNLOAD_FILES = os.environ["DOWNLOAD_FILES"]


#################################
# CLASS TO HANDLE THE SQS QUEUE
#################################


class JobQueue:
    def __init__(self, queueURL):
        self.client = boto3.client("sqs")
        self.queueURL = queueURL

    def readMessage(self):
        response = self.client.receive_message(
            QueueUrl=self.queueURL, WaitTimeSeconds=20
        )
        if "Messages" in response.keys():
            data = json.loads(response["Messages"][0]["Body"])
            handle = response["Messages"][0]["ReceiptHandle"]
            return data, handle
        else:
            return None, None

    def deleteMessage(self, handle):
        self.client.delete_message(QueueUrl=self.queueURL, ReceiptHandle=handle)
        return

    def returnMessage(self, handle):
        self.client.change_message_visibility(
            QueueUrl=self.queueURL, ReceiptHandle=handle, VisibilityTimeout=60
        )
        return


#################################
# AUXILIARY FUNCTIONS
#################################


def monitorAndLog(process, logger):
    while True:
        output = process.stdout.readline().decode()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())
            logger.info(output)


def printandlog(text, logger):
    print(text)
    logger.info(text)


#################################
# RUN SOME PROCESS
#################################


def runSomething(message):
    # Configure the logs
    logger = logging.getLogger(__name__)
    metadataID = message["plate"]

    # Add a handler with
    watchtowerlogger = watchtower.CloudWatchLogHandler(
        log_group=LOG_GROUP_NAME, stream_name=str(metadataID), create_log_group=False
    )
    logger.addHandler(watchtowerlogger)

    # See if this is a message you've already handled, if you've so chosen
    # Check for file with plate name in it
    if CHECK_IF_DONE_BOOL.upper() == "TRUE":
        try:
            s3client = boto3.client("s3")
            bucketlist = s3client.list_objects(
                Bucket=message["output_bucket"], Prefix=message["output_location"]
            )
            objectsizelist = [k["Size"] for k in bucketlist["Contents"]]
            objectsizelist = [i for i in objectsizelist if i >= 1]
            objectsizelist = [i for i in objectsizelist if message["plate"] in i]
            if len(objectsizelist) >= 1:
                printandlog(
                    "File not run because it already exists and CHECK_IF_DONE=True",
                    logger,
                )
                logger.removeHandler(watchtowerlogger)
                return "SUCCESS"
        except KeyError:  # Returned if that folder does not exist
            pass

    # Download files
    printandlog("Downloading files", logger)
    plate_path = os.path.join(message["input_location"], message["plate"])
    local_root = "/home/ubuntu/local"
    local_plate_path = os.path.join(local_root, message["plate"])
    os.makedirs(local_plate_path, exist_ok=True)

    cmd = f'aws s3 cp s3://{message["input_bucket"]}/{plate_path} {local_plate_path} --recursive'
    printandlog(f"Running {cmd}", logger)
    logger.info(cmd)
    subp = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    monitorAndLog(subp, logger)

    # Build and run the program's command
    # Use os.path.join to account for trailing slashes on inputs
    flags = ""
    if message["resolutions"]:
        flags = flags + f" --resolutions {message['resolutions']}"
    if message["tile_width"]:
        flags = flags + f" --tile_width {message['tile_width']}"
    if message["tile_height"]:
        flags = flags + f" --tile_height {message['tile_height']}"
    if message["target-min-size"]:
        flags = flags + f" --target-min-size {message['target-min-size']}"
    if message["additional_flags"]:
        flags = flags + f" {message['additional_flags']}"
    index_path = os.path.join(local_plate_path, message["path_to_metadata"])
    zarr_path = os.path.join(local_root, f"{message['plate']}.ome.zarr")
    cmd = (
        f"/usr/local/bin/_entrypoint.sh bioformats2raw {index_path} {zarr_path} {flags}"
    )

    printandlog(f"Running {cmd}", logger)
    logger.info(cmd)
    subp = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    monitorAndLog(subp, logger)

    printandlog("Finished with .ome.zarr creation.", logger)

    # If done, get the outputs and move them to S3
    s3path = os.path.join(
        message["output_bucket"],
        message["output_location"],
        f"{message['plate']}.ome.zarr",
    )
    with open(os.path.join(zarr_path,'.zattrs')) as f:
        zattrs = json.load(f)
    if 'plate' in zattrs:
        time.sleep(30)
        mvtries = 0
        while mvtries < 3:
            try:
                printandlog("Move attempt #" + str(mvtries + 1), logger)
                if message["upload_flags"]:
                    cmd = f"aws s3 cp {zarr_path} s3://{s3path} {message['upload_flags']} --recursive"
                else:
                    cmd = f"aws s3 cp {zarr_path} s3://{s3path} --recursive"
                printandlog(f"Uploading files with command {cmd}", logger)
                subp = subprocess.Popen(
                    cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                out, err = subp.communicate()
                out = out.decode()
                err = err.decode()
                printandlog("== OUT \n" + out, logger)
                if err == "":
                    break
                else:
                    printandlog("== ERR \n" + err, logger)
                    mvtries += 1
            except:
                printandlog("Move failed", logger)
                printandlog("== ERR \n" + err, logger)
                time.sleep(30)
                mvtries += 1
        if mvtries < 3:
            printandlog("SUCCESS", logger)
            logger.removeHandler(watchtowerlogger)
            return "SUCCESS"
        else:
            printandlog(
                "SYNC PROBLEM. Giving up on trying to sync " + metadataID, logger
            )
            import shutil

            shutil.rmtree(local_root, ignore_errors=True)
            logger.removeHandler(watchtowerlogger)
            return "PROBLEM"
    else:
        printandlog("PROBLEM: Failed exit condition for " + metadataID, logger)
        logger.removeHandler(watchtowerlogger)
        import shutil

        shutil.rmtree(local_root, ignore_errors=True)
        return "PROBLEM"


#################################
# MAIN WORKER LOOP
#################################


def main():
    queue = JobQueue(QUEUE_URL)
    # Main loop. Keep reading messages while they are available in SQS
    while True:
        msg, handle = queue.readMessage()
        if msg is not None:
            result = runSomething(msg)
            if result == "SUCCESS":
                print("Batch completed successfully.")
                queue.deleteMessage(handle)
            else:
                print("Returning message to the queue.")
                queue.returnMessage(handle)
        else:
            print("No messages in the queue")
            break


#################################
# MODULE ENTRY POINT
#################################

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Worker started")
    main()
    print("Worker finished")
