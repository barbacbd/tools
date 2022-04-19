from fedora:latest

# Not building secrets and keys into the DOCKERFILE so that the
# user is forced to copy their own over in the future. These values
# can change and thus should not be added here even in a generic fashion

# update and install new packages
RUN yum update -y
RUN yum install -y \
    jq \
    wget \
    ncurses

# Grab the openshift client, unpack it and move it to the bin for use
RUN \
    wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz \
    && tar -xvzf openshift-client-linux.tar.gz && cp oc /usr/bin/

# move the installation script over to the image so it is available to all
ADD openshift-installer-scripts /