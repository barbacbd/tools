#!/bin/bash

COLOR_OFF='\033[0m'
BLUE='\033[0;34m'

function INFO() {
    echo -e "${BLUE}${1}${COLOR_OFF}"
}

# make the assets directory if it does not exist
if [ ! -d "assets" ]; then
    INFO "Creating assets dir ...";
    mkdir assets;
fi

# copy the install config over in case you have one.
if [ -f "install-config.yaml" ]; then
    INFO "Copying install-config.yaml to assets ...";
    cp install-config.yaml assets/
fi

INFO "Pushin assets on to stack ...";
pushd assets

# Requires openshift-install in your path
openshift-install create cluster

INFO "Popping assets from the stack ...";
popd
