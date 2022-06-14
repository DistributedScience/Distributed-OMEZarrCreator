#
#                                 - [ BROAD'16 ] -
#
# A docker instance for accessing AWS resources
# This wraps the BioFormats2Raw docker registry
#


FROM openmicroscopy/bioformats2raw:0.5.0rc1

# Install S3FS
USER root
RUN apt-get -y update           && \
    apt-get -y upgrade          && \
    apt-get -y install 		\
	automake 		\
	autotools-dev 		\
	g++ 			\
	git 			\
	libcurl4-gnutls-dev 	\
	libfuse-dev 		\
	libssl-dev 		\
	libxml2-dev 		\
	make pkg-config		\
	sysstat			\
	curl

RUN apt install -y python3.9-dev python3.9-distutils python3-pip

# Install AWS CLI
RUN python3.9 -m pip install awscli

# Install boto3

RUN python3.9 -m pip install boto3

# Install watchtower for logging

RUN python3.9 -m pip install watchtower

# SETUP NEW ENTRYPOINT

RUN mkdir -p /home/ubuntu/
WORKDIR /home/ubuntu
COPY B2R-worker.py .
COPY instance-monitor.py .
COPY run-worker.sh .
RUN chmod 755 run-worker.sh

WORKDIR /home/ubuntu
ENTRYPOINT ["./run-worker.sh"]
CMD [""]
