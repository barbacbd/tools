# Instructions and Notes for Installing and using Openshift Ansible

This document will include information for utilizing openshift-ansible and openshift installer to create a cluster.
Throughout the document, AWS will be the platform of choice.

# Related Projects

See the following Projects for references that will be mentioned throughout this document:

- [Pull Secrets](https://github.com/barbacbd/tools/blob/main/references/PullSecret.md)
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

**NOTE**: If the key in OI is the same as the one used for the openshift installer create cluster, then
this process will go smoother. 

4. Add the openshift-installer bin to the path

`export PATH=/path/to/installer/bin:$PATH`

For me this would include

`export PATH=$HOME/dev/installer/bin:$PATH`

The version controlled way to do this (when you want to include multiple versions of the installer) is:

```bash
mv /path/to/installer/bin/openshift-installer /home/$USER/bin
```

This makes the assumption that `/home/$USER/bin` is in your path.


5. Version control openshift client

Similar to step 4 (above), oc or the openshift client software can be version controlled by
moving the file to `/home/$USER/bin`. From this directory we can rename the `oc` with a version
for instance:

```bash
mv oc oc-<version>
mv oc-<version> /home/$USER/bin

cd /home/$USER/bin

ln -s oc-<version> oc
```

Now `oc` will be the version that you want it to be.


6. 



# FAQ

1. What is a bastion?

The bastion was/is a defense mechanism that provides a link or connection to the cluster. An `ssh pod` or bastion is installed
in the cluster so that we can reach the cluster through this pod. It provides a connection to the cluster but access must be
achieved indirectly.

2. Openshift Installer vs Openshift Ansible

Openshift Ansible is generally related to ansible and talked about with versions 3.x. In the past, RHEL nodes were used. After
the acquisition of the product RHCOS, ansible was migrated. There is still a need to install RHEL nodes, and thus openshift
ansible was kept alive and used as a bridge with openshift installer to allow the users to spin up RHEL nodes. The openshift
installer will only utilize RHCOS nodes (which do not have saved state) unless openshift ansible is used after a cluster is
created.

3. Don't forget to destroy your cluster when finished !

4. My oi-byoh.sh script is failing, what next?

4.1 Bastion - Make sure that the oi key is the same. See section above.

4.2 Create -

4.3 Prepare -


5. Problems running oi-byoh.sh.

Using `ansible==2.9.27` failed. Remove this from the computer (at least for now).

Install `libselinux-python3` via yum. This will be picked up as a pip package that you can see as version (>=2.9) via pip3 list. **If you install directly with pip, the version is VERY different.**

Create a virtual environment for python3

```
python3 -m venv ansible-2.10.7 --system-site-packages

pip install pip --upgrade

pip install ansible-base ansible==2.10.7 boto3
```

In order for the commands above to work, ansible needs to be uninstalled or conflicts will occur with `ansible-base`. This is an issue because we also need selinux for python3, and this had to be pulled in from the global package list as we cannot install the correct version.

6. AWS key issues

Go to AWS site, and create new keys or match the keys for each region. If you decide to install to a different region, then that region needs to have a matching key. **You can name the keys the same between regions.**

