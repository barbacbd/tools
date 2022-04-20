import argparse
from logging import getLogger, DEBUG
from getpass import getuser
from os.path import isdir, isfile, exists
from os import mkdir, chmod, stat
from datetime import datetime
from shutil import rmtree
import stat as STAT
from pathlib import Path


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


def gen_platform_envvars(platform, *args, **kwargs):
    """
    Generate the environment variables that are necessary for the platform

    :param platform: See argparse for supported platforms
    :return: List of statements that will be added to the docker file tagged with `ENV`
    """
    data = {
        "aws": [
            "AWS_PROFILE={}".format(kwargs.get("AWS_PROFILE", "openshift-dev"))
        ],
        "gcp": [
            "GOOGLE_APPLICATION_CREDENTIALS={}".format(
                kwargs.get("GOOGLE_APPLICATION_CREDENTIALS", "/home/{}/.gcp/gcp-key.json".format(getuser()))
            )
        ]
    }.get(platform, [])

    for i in range(len(data)):
        data[i] = "ENV " + data[i]

    return data


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

# move the installation script over to the image so it is available to all
RUN mkdir scripts
ADD scripts /scripts

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
pullSecret: {}                                                                                                                                                                                              
sshKey: |
  {}
    """.format(
        cluster_name,
        platform,
        region,
        secrets,
        ssh_key
    )
    with open("{}/install-config.yaml".format(generation_dir), 'w+') as install_config:
        install_config.write(install_config_data)
        

def generate_install_in_container_script():
    # generate a script that will be added to the container
    data = """#!/bin/bash
./openshift-install create cluster --dir /cluster --log-level debug
    """
    script_name = "{}/scripts/install.sh".format(generation_dir)
    
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
    

podman run --rm -it                               \\
    -v "/home/{}/clusters/{}/{}":/cluster/        \\
    -v $installer_binary:/openshift-install    \\
    -v "/home/{}/.{}":/.{}                         \\
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

    script_name = "{}/installer.sh".format(generation_dir)

    with open(script_name, 'w+') as ifile:
        ifile.write(data)

    p = Path(script_name)
    p.chmod(p.stat().st_mode | STAT.S_IEXEC) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate the necessary files for"
                                     " creating the docker/podman image for the openshift installer"
    )

    parser.add_argument(
        '-d', '--dir',
        help='Directory containing credentials information, default will be /home/user/.<platform>',
        type=str,
        default=None
    )
    parser.add_argument(
        'ssh_key',
        help='File containing the ssh key that the user will utilize',
        type=str
    )
    parser.add_argument(
        'secrets',
        help='File containing the secrets that the user will utilize',
        type=str
    )
    parser.add_argument(
        '-p', '--platform',
        help='Supported cloud platform to configure',
        type=str,
        choices=['aws', 'gcp'],
        default='aws'
    )
    parser.add_argument(
        '-r', '--region',
        help='Platform region to use for configuration',
        type=str,
        default=None
    )
    parser.add_argument(
        '--aws_profile',
        help='Only appliable to aws, AWS Profile Settings, found in aws config',
        type=str,
        default='openshift-dev'
    )
    parser.add_argument(
        '--google_creds',
        help='Only appliable to gcp, GCP App Creds file',
        type=str,
        default="/home/{}/.gcp/gcp-key.json".format(getuser())
    )
    parser.add_argument(
        '--os_image_name',
        help='path/name of the Openshift image to use',
        type=str,
        default='quay.io/openshift-release-dev/ocp-release:4.10.10.x86_64'
    )
    parser.add_argument(
        '--custom_image_name',
        help='name of the image that will be created from the dockerfile',
        type=str,
        default='installer-wwt'
    )
    parser.add_argument(
        '--custom_image_tag',
        help='tag for the image that will be created from the dockerfile',
        type=str,
        default='latest'
    )
    parser.add_argument(
        '--installer_dir',
        help='Base directory for the local openshift installer code.',
        type=str,
        default='/home/{}/dev/installer'.format(getuser())
    )
    
    args = parser.parse_args()

    # read in the ssh data from the file
    ssh_info = None
    if exists(args.ssh_key) and isfile(args.ssh_key):
        with open(args.ssh_key, 'r') as ssh_file:
            ssh_info = ssh_file.read()
    else:
        log.error("Invalid ssh key file")
        exit(1)

    if ssh_info is None:
        log.error("No ssh info found")
        exit(2)

    # read in the secrets data from the file
    secrets_info = None
    if exists(args.secrets) and isfile(args.secrets):
        with open(args.secrets, 'r') as secrets_file:
            secrets_info = secrets_file.read()
    else:
        log.error("Invalid secrets file")
        exit(3)

    if secrets_info is None:
        log.error("No secrets info found")
        exit(4)

    creds_dir = args.dir
    if creds_dir is None:
        creds_dir = "/home/{}/.{}".format(getuser(), args.platform)
        log.debug("Set the credentials directory to {}".format(creds_dir))

    if not isdir(creds_dir):
        log.error("{} does not exist".format(creds_dir))
        exit(1)

    region = args.region
    if region is None:
       region = {
           "aws": "us-east-1",
           "gcp": "us-east1"
       }.get(args.platform)

    log.debug("Region is set to {}".format(region))

    # reebuild the generation directory where the data should reside
    if isdir(generation_dir):
        log.warning("Removing all data from {}".format(generation_dir))
        rmtree(generation_dir)
        
    mkdir(generation_dir)
    # create the dir where extra scripts will reside
    mkdir("{}/scripts".format(generation_dir))

    # datetime string that can be used for several functions if needed
    # this will control the name of the clusters and directories
    dt = datetime.now().strftime("%Y%m%d")

    generate_install_config(
        "{}-{}-{}".format(getuser(), args.platform, dt),
        args.platform,
        region,
        ssh_info,
        secrets_info
    )

    generate_install_in_container_script()
    generate_install_base_install_script(
        args.platform,
        args.installer_dir,
        args.os_image_name,
        args.custom_image_name,
        args.custom_image_tag,
        dt
    )

    # base packages + platform specific
    packs = ["jq", "wget", "ncurses"] + get_custom_packages(args.platform)

    # supply everything that we have, doesn't matter on the platform, the function
    # will choose what it needs
    envvars = gen_platform_envvars(
        args.platform,
        AWS_PROFILE=args.aws_profile,
        GOOGLE_APPLICATION_CREDENTIALS=args.google_creds
    )

    extra_df_statements = generate_dockerfile_statements(args.platform)

    generate_dockerfile(packs, envvars, extra_df_statements)
    
