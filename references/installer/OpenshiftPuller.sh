#!/bin/bash

version=""

while true; do
    read -p "Would you like to pull the latest [y/N]? " use_latest
    case $use_latest in
	[Yy]* ) version="latest"; break;;
	[Nn]* )
	    read -p "What oc version would you like? " version;
	    break;;
	* ) echo "Please answer yes or no.";;
    esac
done

mkdir openshift_puller_tmp;
pushd openshift_puller_tmp;
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$version/openshift-client-linux.tar.gz;
tar -xvzf openshift-client-linux.tar.gz;

# get the version, this will handle the case of 'latest' too
retrieved_version=$(./oc version | head -n 1 | awk '{print $3}')

# rename the OC with the version 
mv oc oc-$retrieved_version
# move the kube control executable over too
mv kubectl /home/$USER/bin

mv oc-$retrieved_version /home/$USER/bin
pushd /home/$USER/bin

# unlink any current OC symlink
if [ -f oc ]; then
    unlink oc
fi

# create a symlink to the retreived version of OC
ln -s oc-$retrieved_version oc

# go back to where we were 
popd
popd

# remove the dir that we created
rm -rf openshift_puller_tmp
