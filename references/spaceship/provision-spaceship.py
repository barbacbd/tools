from os import listdir, remove, rename
from os.path import exists
from inquirer import prompt, list_input, text, password
from jinja2 import Environment, FileSystemLoader, Template
from shutil import copyfile

"""
HOW TO:

python requirements: python3.6 >=

system requirements: 
 - SSH Key generated for github use
 - 

provision: 
 - python3 -m venv venv;
 - pip install pip --upgrade
 - pip install -r requirements.txt
 - python provision-spaceship.py
   - << Fill in information >> 

Podman/Docker:
 - podman build -t spaceship:latest .
 - podman run -it spaceship:latest /bin/bash

Entry:
 - ./init.sh
 - ./configure.sh

The artifacts of running this script include:
- ssh-key
- Dockerfile

**Please do NOT add these files to any publically hosted project!**
"""

WARNING="""#########################################################
# This is an auto-generated file. 
# Do NOT Edit.
# All edits will be removed during provisioning.
#########################################################
"""

# assumes that the current user is the one 
docker_key_file_name = "ssh-key"

# prompt the user for some input
# The file directory should be the full path to the files: /home/USER/.ssh
file_dir = text(message="Path to ssh key files")
keyfile = list_input(message='Select your ssh key file', choices=listdir(file_dir))
user = text(message="git username")

# remove the original ssh-key file if it existed
if exists(docker_key_file_name):
    remove(docker_key_file_name)

# full filename of the file to copy
copied_file = "{}/{}".format(file_dir, keyfile)
# copy the original file to the contents of the file 'ssh-key'
copyfile(copied_file, "./{}".format(docker_key_file_name))

# Remove the Dockerfile if it exists currently, this way no stale data exists
if exists("Dockerfile"):
    remove("Dockerfile")

# Take the j2 template and fill in the information with what we created,
# then write the data to `Dockerfile`
with open("Dockerfile.j2", "r") as jfile:
    template = Template(jfile.read())

# fill in the template
# New variables can be added here
output = template.render({"user": user, "WARNING": WARNING})

# write the template
# The user can now run:
# podman build -t spaceship:latest .
# ...
# Note: replacing podman with docker is reasonable if docker is desired
with open("Dockerfile", "w+") as ic:
    ic.write(output)
