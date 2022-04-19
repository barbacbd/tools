#!/bin/bash

options=("aws" "gcp")
cur_dir=$(pwd)
my_user=$(whoami)

help() {
    echo "Installer setup script:"
    echo
    echo "Syntax: installer.sh [p|c|h]"
    echo "options:"
    echo "-h      Print Help"
    echo "-p      Cloud Platform (${options[@]})"
    echo
}

while getopts p:c:h flag
do
    case "${flag}" in
        p) proj_type=${OPTARG};;
	h)
            help
            exit
            ;;
    esac
done

dt=$(date +%Y%m%d);
cluster_dir=$HOME/test-clusters/$dt-$proj_type
cluster_name=$my_user-$proj_type-$dt
ssh_key=$(cat $HOME/.ssh/id_ed25519.pub)
secrets=$(cat $HOME/.docker/config.json)


# copy the file to the cluster directory. Alternatively we could create
# a config with `openshift-install create install-config`
cat >> install-config.yaml << EOF
apiVersion: v1
baseDomain: devcluster.openshift.com
compute:
- architecture: amd64
  hyperthreading: Enabled
  name: worker
  platform: {}
  replicas: 3
controlPlane:
  architecture: amd64
  hyperthreading: Enabled
  name: master
  platform: {}
  replicas: 3
metadata:
  name: $cluster_name
platform:
  $proj_type:
    region: us-east-1
publish: External
pullSecret: $secrets
sshKey: |
  $ssh_key
EOF
