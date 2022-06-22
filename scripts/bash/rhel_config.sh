#!/bin/bash

#######################################################################
# Configuration script for initializing some basic setup on RHEL.
# This script _could_ be used for multiple platforms, but the only
# tested platform is RHEL 8.
#######################################################################

# bash file used for profiling information
BASHRC=$HOME/.bashrc
BASHPROFILE=$HOME/.bash_profile


# Log Level Functions
INFO()  { echo "[INFO]:  $1"; }
DEBUG() { echo "[DEBUG]  $1"; }
WARN()  { echo "[WARN]:  $1"; }
ERROR() { echo "[ERROR]: $1"; }


# Function will take 3 args (generally):
# $1: title that will be displayed in the form of a question. No need for options
#     or the question mark.
# $2: The function that will be used in the event of Y option [optional]
# $3: The function that will be used in the event of N option [optional]
function readAndExecute(){
    while true; do
	read -p "$1 [y/N]? " ans
	
	case $ans in
	    "" ) ;&
            [Nn]* )
		if [ $# -eq 3 ] ; then
		    "$3";
		fi
		break;;
	    
	    [Yy]* )
		if [ $# -ge 2 ] ; then
		    "$2";
		else
		    DEBUG "Missing parameter 2, the function for case Y.";
		fi
		break;;
	esac
    done
}

function installVim () { sudo yum install -y vim; }
function addEmacsShortcut() { echo "alias emacs='emacs -nw'" >> $BASHRC;}
function sshKeyGenRSA () { ssh-keygen -t rsa -b 4096; }
function sshKeyGenED () { ssh-keygen -t ed25519; }
function generateSSHKey() { readAndExecute "Does your system support the ED25519 algorithm" sshKeyGenED sshKeyGenRSA; }
function gcloudInit () { gcloud init; }
function installEmacs() {
    sudo yum install -y emacs;
    readAndInstall "Would you like to add the -nw option for emacs" addEmacsShortcut
}

# Generate a GPG private key
function generateGPGKey() {
    DEBUG "Generating GPG Key, follow the instructions carefully."
    if [ $UPDATED_GPG -eq 1 ]; then
	WARN "Use 4096 for the size or the key cannot be used."
	gpg --full-generate-key;
    else
	gpg --default-new-key-algo rsa4096 --gen-key;
    fi
}

# Generate a set of files, one for each GPG private key currently saved
function generateGPGPublicFiles() {
    DEBUG "GENERATING GPG Secret information ...";
    keys=$(gpg --list-secret-keys --with-colons | awk -F: '$1 == "sec" {print $5}');
    
    if [[ "$(declare -p keys)" =~ "declare -a" ]]; then
	for key in "${keys[@]}"
	do
	    : 
	    gpg --armor --export "$HOME/Desktop/$key.pub";
	done
    else
	gpg --armor --export $keys >> "$HOME/Desktop/$keys.pub";
    fi
   
    INFO "GPG Public Key files can be found in $HOME/Desktop";
}

# Copy all local credential files to a location that mirrors the
# name of the cloud platform. For instance, pass "aws" for the
# aws information
function moveCloudCreds () {
    if [ -d "./$1" ] ; then
	DEBUG "Found $1 information";
	
	if [ ! -d "$HOME/.$1" ] ; then
	    mkdir $HOME/.aws
	else
	    WARN "$HOME/.$1 exists, check that files are not replaced ... ";
	fi
	
	for f in "./$1/*"
	do
	    DEBUG "Copying $f to $HOME/.$1";
	done
	
	cp ./$1/* $HOME/.$1;
    fi   
}

function installGcloud() {
    DEBUG "Installing and configuring gcloud";
    cd $HOME/Downloads;
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-381.0.0-linux-x86_64.tar.gz;
    tar -xvzf google-cloud-sdk-381.0.0-linux-x86.tar.gz;
    ./google-cloud-sdk/install.sh;
    
    source $BASHRC;

    readAndExecute "Would you like to run the initialization" gcloudInit
}


##############################################################################
# Main Script
##############################################################################

INFO "Updating the system ...";
sudo yum update -y;

# Install text editors
# personally I am a fan of emacs, so that will come in to play
# but most trend towards vim
readAndExecute "Do you wish to install vim" installVim
readAndExecute "Do you wish to install emacs" installEmacs


# Add other shortcuts to the bashrc file
INFO "Adding other shortcuts to the bashrc file";

echo "# Command to remove all temp files created by emacs." >> $BASHRC;
echo "alias clean='rm -rf *~'" >> $BASHRC;


# Generate an RSA key
# Note: only a single key is generated, please execute on your own if you desire more
INFO "Generating an SSH key(s)."
DEBUG "Please follow the text carefully to ensure that your information is correct."

readAndExecute "Would you like to generate a[nother] key" generateSSHKey

# install GPGme and generate a GPG Key
INFO "Installing GPGME and beginning the GPG key configuration."

sudo yum install -y gpgme;

INFO "Adding shortcuts for the gpg key information.";
echo "" >> $BASHRC;
echo "############################################## " >> $BASHRC;
echo "# GPG commands for convenience " >> $BASHRC;
echo "############################################## " >> $BASHRC;
echo "# The following command will list all secret keys (see below)" >> $BASHRC;
echo "alias gpg-secret='gpg --list-secret-keys --keyid-format LONG'" >> $BASHRC;
echo "# The following command should be supplied with the keyid from secret output" >> $BASHRC;
echo "alias gpg-public='gpg --armor --export'" >> $BASHRC;

# source the file so that we can use the information we just stored
source $BASHRC;

# determine the command to use for the GPG key generation
if [[ "$x" > "2.1.16" ]]; then UPDATED_GPG=1; else UPDATED_GPG=0; fi

readAndExecute "Would you like to generate a[nother] gpg-key" generateGPGKey
readAndExecute "Would you like to generate public gpg files" generateGPGPublicFiles


# setup some personally preferenced spaces for whatever
DEBUG "Creating personal choiced spaces."

# add future dirs here 
personal_dirs=("$HOME/dev" "$HOME/personal")
for pd in ${personal_dirs[@]}; do
    if [ ! -d $pd ] ; then
	mkdir $pd
	DEBUG "Created $pd.";
    else
	WARN "$pd already exists, skipping ...";
    fi
done

# Add the following keyboard shortcuts
# {"name: "terminal", "command": "gnome-terminal", "shortcut": "<Primary><STRL><ALT><T>"}
# {"name": "Maximize window horizontally", "command": "", "shortcut": "<Primary><CTRL><right>"}
# {"name": "Maximize window vertically", "command": "", "shortcut": "<Primary><CTRL><up>"}

# https://askubuntu.com/questions/597395/how-to-set-custom-keyboard-shortcuts-from-terminal
#
#INFO "Creating and Adding Keyboard shortcuts";
#DEBUG "Keyboard shortcuts take a bit to load, adding to the bash profile";


#################################################################
# Create or initialize gloud account access
# Note: These will be added as needed. Credential files
# Are NOT generated here, rather the user can add them to
# predetermined directories in the same directory as this file
# For example, aws credentials should be placed into a file in a
# directory called ./aws.
#################################################################

#################################################################
# AWS
#################################################################
moveCloudCreds "aws"

#################################################################
# GCP
#################################################################
moveCloudCreds "gcp"
readAndExecute "Would you like to install gcloud" installGcloud

