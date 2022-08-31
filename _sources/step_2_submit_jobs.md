# Step 2: Submit Jobs

Distributed-OMEZARRCreator batches jobs by plate so no matter how large your list of plates to process, each EC2 instance will process one job = one plate.
Once your job file is configured, simply use `python run.py submitJob files/{YourJobFile}.json` to send all the jobs to the SQS queue [specified in your config file](step_1_configuration.md).

## Configuring your job file

All keys (other than "plates") are shared between all jobs.
The examples below are provided for a folder structure as follows:  

s3://BUCKET  
└── PROJECTNAME  
&emsp;&emsp;&emsp;└── SOURCE  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;└──images  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;└── BATCHNAME  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;└── images  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;├── PLATE1  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; |&emsp;&emsp;&emsp;└──Images  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; |&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;└──Index.idx.xml  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; |&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; └──r01c01f01p01-ch1sk1fk1fl1.tiff  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; |&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; └──r01c01f01p01-ch2sk1fk1fl1.tiff  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;└── PLATE2

* **input_bucket:** The bucket where your input images are.
* **input_location:** The path to your input images on your input_bucket.
The parent folder of your plate folders.
(e.g. `PROJECTNAME/SOURCE/images/BATCHNAME/images/`)
* **path_to_metadata:** Within each plate folder, the path to the metadata file.
(e.g. `Images/Index.idx.xml`)
* **output_bucket:** The bucket where you would like to upload your finished .ome.zarr files.
* **output_location:** The parent folder of your .ome.zarr's on your output bucket.
(e.g. `PROJECTNAME/SOURCE/images/BATCHNAME/images_zarr/`)
* **upload_flags:** Enter any flags you want passed to s3 for upload.
Otherwise set to `false`.
(e.g. `--acl bucket-owner-full-control --request-payer requester --metadata-directive REPLACE`)
* **resolutions:** Enter a value if you want to pass resolutions to BioFormats2Raw.
Otherwise set to `false`.
(e.g. `6`)
* **tile_width:** Enter a value if you want to pass a maximum tile width to BioFormats2Raw.
Otherwise set to `false`.
(e.g. `512`)
* **tile_height:** Enter a value if you want to pass a maximum tile height to BioFormats2Raw.
Otherwise set to `false`.
(e.g. `512`)
* **target-min-size:** Enter a value if you want to pass target minimum size to BioFormats2Raw.
Otherwise set to `false`.
(e.g. `2160`)
* **additional_flags:** Enter any additional flags you want passed to BioFormats2Raw.
Otherwise set to `false`.
(e.g. `--extra-readers com.glencoesoftware.bioformats2raw.MiraxReader --series 0,2,3,4`)
* **plates:** The list of all the plates you'd like to process.
Each plate is an individual task and will be run in parallel.
(e.g. `["PLATE1", "PLATE2", "PLATE3"]`)
