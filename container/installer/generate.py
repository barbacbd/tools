import argparse
from logging import getLogger, DEBUG
from getpass import getuser
from os.path import isdir, isfile, exists
from os import mkdir, chmod, stat
from datetime import datetime
from shutil import rmtree
import stat as STAT
from pathlib import Path
from yaml import safe_load


log = getLogger()
log.setLevel(DEBUG)


generation_dir = "openshift-installer-data"

def get_custom_packages(platform):
    """
    A cloud platform may require additional packages to be installed via yum/dnf. Add
    a list of those here for the platform.
    """
    return {
        "aws": ['awscli']
    }.get(platform, [])


def generate_dockerfile_statements(platform):
    """
    A cloud platform may require additional packages or commands. Add
    a list of those here for the platform.
    """
    statements = []

    if platform == "gcp":
        statements.extend([
            'RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-382.0.0-linux-x86_64.tar.gz',
            'RUN -xf google-cloud-cli-382.0.0-linux-x86.tar.gz',
            'RUN ./google-cloud-sdk/install.sh'
        ])

    return statements


def generate_dockerfile(packs, envvars, extra_commands):
    """
    Generate the docker file.

    :param packs: List of packages to install
    :param envvars: list of environment variables to add to the image
    :param extra_commands: List of extra commands added to the end of the file, see `generate_dockerfile_statements`
    """
    init_dockerfile_data = """from fedora:latest

# Not building secrets and keys into the DOCKERFILE so that the
# user is forced to copy their own over in the future. These values
# can change and thus should not be added here even in a generic fashion

# update and install new packages
RUN yum update -y
RUN yum install -y {}

# Grab the openshift client, unpack it and move it to the bin for use
RUN wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz && tar -xvzf openshift-client-linux.tar.gz && cp oc /usr/bin/

# set the cluster directory where the information will be used for the installer
ADD install.sh /install.sh
RUN mkdir /cluster
ADD install-config.yaml /cluster/install-config.yaml

# added environment variables
{}

{}
    """.format(
        " ".join(packs),
        "\n".join(envvars),
        "\n".join(extra_commands)
    )

    with open("{}/Dockerfile".format(generation_dir), "w+") as dfile:
        dfile.write(init_dockerfile_data)


def generate_install_config(cluster_name, platform, region, ssh_key, secrets):
    """
    Generate an install-config, similar to running `openshift-installer create install-config`

    :param cluster_name: name of the cluster
    :param platform: cloud platform in use
    :param region: region from that platform
    :param ssh_key: data from the public ssh key file
    :param secrets: data from the secrets file.
    """
    install_config_data = """apiVersion: v1
baseDomain: devcluster.openshift.com
compute:
- architecture: amd64
  hyperthreading: Enabled
  name: worker
  replicas: 3
controlPlane:
  architecture: amd64
  hyperthreading: Enabled
  name: master
  replicas: 3
metadata:
  name: {}
platform:
  {}:
    region: {}
publish: External
pullSecret: '{}'
sshKey: |
  {}
"""

    with open("{}/install-config.yaml".format(generation_dir), 'w+') as install_config:
        install_config.write(install_config_data.format(cluster_name, platform, region, secrets, ssh_key))
        

def generate_install_in_container_script():
    # generate a script that will be added to the container
    data = """#!/bin/bash
./openshift-install create cluster --dir /cluster --log-level debug
    """
    script_name = "{}/install.sh".format(generation_dir)
    
    with open(script_name, "w+") as ifile:
        ifile.write(data)

    p = Path(script_name)
    p.chmod(p.stat().st_mode | STAT.S_IEXEC) 

def generate_install_base_install_script(platform, os_installer_dir, os_image_name, custom_image_name, custom_image_tag, date_str):
    # generate the script that will be used to create a container from the image
    data = """#!/bin/bash

set -eux

src_dir={}
installer_binary=$src_dir/bin/openshift-install
    
#    -v "/home/{}/clusters/{}/{}":/cluster/        \\
podman run --rm -it                               \\
    -v $installer_binary:/openshift-install    \\
    -v "/home/{}/.{}":/root/.{}                         \\
    -e OPENSHIFT_INSTALL_RELEASE_IMAGE_OVERRIDE={} \\
    -e KUBECONFIG="/c/auth/kubeconfig"             \\
    {}:{} /bin/bash
    """.format(
        os_installer_dir, # pre podman-command  
        getuser(), platform, date_str, # line 2
        getuser(), platform, platform, # line 4
        os_image_name, # line 5
        custom_image_name, custom_image_tag # line 7
    )

    script_name = "{}/connect.sh".format(generation_dir)

    with open(script_name, 'w+') as ifile:
        ifile.write(data)

    p = Path(script_name)
    p.chmod(p.stat().st_mode | STAT.S_IEXEC) 

if __name__ == "__main__":
    with open("config.yaml", "r") as config:
        yaml_data = safe_load(config)

    ssh_file = yaml_data["ssh_key_file"]
    
    # read in the ssh data from the file
    ssh_info = None
    if exists(ssh_file) and isfile(ssh_file):
        with open(ssh_file, 'r') as s:
            ssh_info = s.read()
    else:
        log.error("Invalid ssh key file")
        exit(1)

    if ssh_info is None:
        log.error("No ssh info found")
        exit(2)

    secrets_file = yaml_data["secrets_file"]
    # read in the secrets data from the file
    secrets_info = None
    if exists(secrets_file) and isfile(secrets_file):
        with open(secrets_file, 'r') as s:
            secrets_info = s.read()
    else:
        log.error("Invalid secrets file")
        exit(3)

    if secrets_info is None:
        log.error("No secrets info found")
        exit(4)

    platform = yaml_data["platform"]
    region = yaml_data["region"]


    installer_dir = yaml_data["installer"]["dir"]
    os_image = yaml_data["installer"]["image"]

    docker_image_name = yaml_data["docker"]["image_name"]
    docker_image_tag = yaml_data["docker"]["tag"]
    
    creds_dir = "/home/{}/.{}".format(getuser(), platform)
    log.debug("Set the credentials directory to {}".format(creds_dir))

    if not isdir(creds_dir):
        log.error("{} does not exist".format(creds_dir))
        exit(1)

    log.debug("Region is set to {}".format(region))

    # reebuild the generation directory where the data should reside
    if isdir(generation_dir):
        log.warning("Removing all data from {}".format(generation_dir))
        rmtree(generation_dir)
        
    mkdir(generation_dir)
    # create the dir where extra scripts will reside
    mkdir("{}/cluster".format(generation_dir))

    # datetime string that can be used for several functions if needed
    # this will control the name of the clusters and directories
    dt = datetime.now().strftime("%Y%m%d")

    generate_install_config(
        "{}-{}-{}".format(getuser(), platform, dt),
        platform,
        region,
        ssh_info,
        secrets_info
    )

    generate_install_in_container_script()
    generate_install_base_install_script(
        platform,
        installer_dir,
        os_image,
        docker_image_name,
        docker_image_tag,
        dt
    )

    # base packages + platform specific
    packs = ["jq", "wget", "ncurses"] + get_custom_packages(platform)

    # supply everything that we have, doesn't matter on the platform, the function
    # will choose what it needs
    envvars = ["ENV {}={}".format(k, v) for k, v in yaml_data["env"].items()]

    extra_df_statements = generate_dockerfile_statements(platform)

    generate_dockerfile(packs, envvars, extra_df_statements)
    

    print("Execute the following command:\n")
    print("cd {} && podman build . -t {}:{}".format(generation_dir, docker_image_name, docker_image_tag))
