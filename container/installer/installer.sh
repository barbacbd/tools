#!/bin/bash

options=("aws" "gcp")
cur_dir=$(pwd)
my_user=$(whoami)

help() {
    echo "Installer setup script:"
    echo
    echo "Syntax: installer.sh [p|c|h]"
    echo "options:"
    echo "-c      Credentials file, default files are assumed in /home/user/.<cloud_platform>/"
    echo "-h      Print Help"
    echo "-p      Cloud Platform (${options[@]})"
    echo
}

while getopts p:c:h flag
do
    case "${flag}" in
	p) proj_type=${OPTARG};;
	c) creds_file=${OPTARG};;
	h)
	    help
	    exit
	    ;;
    esac
done

if [[ ! " ${options[*]} " =~ " ${proj_type} " ]]; then
    # provide options for the possible platforms
    cloud_platform='Please choose the index for the cloud platform: '
    
    select opt in "${options[@]}"
    do
	case $opt in
            "aws")
		proj_type=$opt;

		break
		;;
            "gcp")
		proj_type=$opt
		
		break
		;;
	    *)
		echo "[ERROR] Unsupported platform";
		exit
		;;
	esac
    done
fi

echo "[DEBUG] selected $proj_type"    
echo "[DEBUG] default credentials file is $creds_file"

# this should be a file containing the credentials in the local directory .${proj_type}
if [ -z ${creds_file+x} ] ; then

    case $proj_type in
	"aws")
	    creds_file=$HOME/.$opt/credentials;
	    break ;;
	"gcp")
	    creds_file=$HOME/.$opt/osServiceAccount.json;
	    break ;;
	*)
	    exit;;
    esac
fi

echo "[DEBUG] credentials file is $creds_file"

local_image="localhost/bbarbach"
local_image_tag="latest"

# change the source directory below in the event of a change to the user and/or location of the project
src_dir=$HOME/dev/installer
installer_binary=$src_dir/bin/openshift-install

# change the name of the image here depending on the tests to be run.
image_name=quay.io/openshift-release-dev/ocp-release:4.10.10.x86_64

pushd $src_dir && ./hack/build.sh && popd

podman run --rm -it \
       -v $installer_binary:/openshift-install                                \
       -v /$HOME/.$proj_type:/.$proj_type                                     \
       -e OPENSHIFT_INSTALL_RELEASE_IMAGE_OVERRIDE=$image_name                \
       -e KUBECONFIG="/c/auth/kubeconfig"                                     \
       $local_image:$local_image_tag /bin/bash
