# Instructions and Notes for Installing and using Openshift Ansible

This document will include information for utilizing openshift-ansible and openshift installer to create a cluster.
Throughout the document, AWS will be the platform of choice.

# Related Projects

See the following Projects for references that will be mentioned throughout this document:

[OI-Dev](https://github.com/jstuever/oi-dev)
[OA-Testing](https://github.com/mtnbikenc/oa-testing)
[Openshift Installer](https://github.com/openshift/installer)
[Openshift Ansible](https://github.com/openshift/openshift-ansible)

# Process

1. Create a cluster using openshift-installer.

```bash
cd /path/to/installer/;

hack/build.sh;

bin/openshift-installer create cluster

```

Go through the process of creating a cluster for AWS.


2. Ensure that there is an ssh key called `oi`.

There should be a matching public key called `oi.pub`. It is ok to **copy** the
ssh key that you normally use. DO NOT sim-link the keys as this could create issues if you
ever remove the keys or change them.

