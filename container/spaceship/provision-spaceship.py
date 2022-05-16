from os import listdir, remove, rename
from os.path import exists
from getpass import getuser
from inquirer import prompt, list_input, text, password
from jinja2 import Environment, FileSystemLoader, Template
from shutil import copyfile



file_dir = "/home/{}/.ssh".format(getuser())
docker_key_file_name = "ssh-key"

account_type = list_input('Account type', choices=['ssh', 'user'])
if account_type == 'ssh':
    keyfile = list_input(message='Select your ssh key file', choices=listdir(file_dir))
else:
    """
    Future work, but GIT username and password are NOT currently
    supported. Any user that wishes to use this project is
    required to add ssh keys to their git account.
    """
    print("You have selected an unavailable option")
    exit(1)
    #username = text(message='Git username')
    #pword = password(message='Git password')

if exists(docker_key_file_name):
    remove(docker_key_file_name)

copied_file = "{}/{}".format(file_dir, keyfile)
copyfile(copied_file, "./{}".format(docker_key_file_name))
#rename(keyfile, docker_key_file_name)
    
user = text(message="git username")
branch = text(message="project branch")

if exists("Dockerfile"):
    remove("Dockerfile")
    
with open("Dockerfile.j2", "r") as jfile:
    template = Template(jfile.read())
output = template.render({"user": user, "branch": branch})
with open("Dockerfile", "w+") as ic:
    ic.write(output)
