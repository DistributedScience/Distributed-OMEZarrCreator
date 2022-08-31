# Troubleshooting

## Troubleshooting Distributed-OMEZARRCreator

| SQS  | CloudWatch   |  S3 | EC2/ECS  | Problem  | Solution |
|---|---|---|---|---|---|
|   | Within a single log, your run command is logging multiple times. | Expected output seen. |   | A single job is being processed multiple times. | SQS_MESSAGE_VISIBILITY is set too short. See SQS-QUEUE-INFORMATION for more information. |
|   |   |   | Machines made in EC2 and dockers are made in ECS but the dockers are not placed on the machines. | There is a mismatch in your DS config file. |  Confirm that the MEMORY matches the MACHINE_TYPE  set in your config. |


## Troubleshooting BioFormats2Raw

We cannot provide comprehensive support for troubleshooting BioFormats2Raw, but we have assembled a few tips below.
See documentation at [BioFormats2Raw](https://github.com/glencoesoftware/bioformats2raw) for more.

There are many ways to test that your .ome.zarr's have been created properly. A few options are as follows:

### Locally using ome-zarr-py:
* Install [ome-zarr-py](https://github.com/ome/ome-zarr-py) by running `pip install ome-zarr`.
* Download an .ome.zarr from your output_bucket.
* Run `ome_zarr info /path/to/file/PLATE.ome.zarr`
You should get an output similar to

```
/path/to/file/SQ00014812__2016-05-23T20_44_31-Measurement1.ome.zarr [zgroup]

metadata
   - Plate

data
   (1, 5, 1, 2160, 3240)
```


* Run `ome_zarr info /path/to/file/PLATE.ome.zarr/0/0/0`.  
You should get an output similar to

```
/path/to/file/SQ00014812__2016-05-23T20_44_31-Measurement1.ome.zarr/0/0/0 [zgroup]

metadata
    Multiscales

data
   (1, 5, 1, 2160, 2160)  
   (1, 5, 1, 1080, 1080)  
   (1, 5, 1, 540, 540)  
   (1, 5, 1, 270, 270)  
   (1, 5, 1, 135, 135)  
```

### Remotely using ome-ngff-validator:
* Edit the following path to your plate of interest and open the path in browser window.
https://ome.github.io/ome-ngff-validator/?source=https://BUCKET.s3.amazonaws.com/path/to/your/omezarr/PLATE.ome.zarr/
