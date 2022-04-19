#!/bin/bash



if [ ! -d "/cluster" ] ; then
   mkdir /cluster
fi

./openshift-install create cluster --dir /cluster --log-level debug
