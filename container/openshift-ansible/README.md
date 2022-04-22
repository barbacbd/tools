# Instructions and Notes for Installing and using Openshift Ansible

This document will include information for utilizing openshift-ansible and openshift installer to create a cluster.
Throughout the document, AWS will be the platform of choice.

# Related Projects

See the following Projects for references that will be mentioned throughout this document:

- [Pull Secrets](./PullSecrets.md)
- [OA-Testing](https://github.com/mtnbikenc/oa-testing) - Utilities to install clusters to aws utilizing openshift-ansible
- [OI-Dev](https://github.com/jstuever/oi-dev) - Simpler cluster installation utilizing openshift-ansible
- [Openshift Installer](https://github.com/openshift/installer)
- [Openshift Ansible](https://github.com/openshift/openshift-ansible)


# Process

1. Make a directory called `assets` in `oi-dev`

The assets directory is the default where the installation should occur for the `oi-dev` project to
utilize openshift-installer information.

2. Create a cluster using openshift-installer.

```bash
cd /path/to/installer/;

hack/build.sh;

bin/openshift-installer create cluster --dir /path/to/assets

```

Go through the process of creating a cluster for AWS.


3. Ensure that there is an ssh key called `oi`.

There should be a matching public key called `oi.pub`. It is ok to **copy** the
ssh key that you normally use. DO NOT sim-link the keys as this could create issues if you
ever remove the keys or change them.


4. Add the openshift-installer bin to the path

`export PATH=/path/to/installer/bin:$PATH`

For me this would include

`export PATH=$HOME/dev/installer/bin:$PATH`


# FAQ

1. What is a bastion?

The bastion was/is a defense mechanism that provides a link or connection to the cluster. An `ssh pod` or bastion is installed
in the cluster so that we can reach the cluster through this pod. It provides a connection to the cluster but access must be
achieved indirectly.