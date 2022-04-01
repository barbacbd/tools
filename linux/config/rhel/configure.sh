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

INFO "Updating the system ...";
sudo yum update -y;


# Install text editors
# personally I am a fan of emacs, so that will come in to play
# but most trend towards vim

while true; do
    read -p "Do you wish to install vim [y/N]? " ans
    case $ans in
	[Yy]* )
	    INFO "Installing vim";
	    sudo yum install -y vim;
	    break;;
	"" ) ;&  # fall through
	[Nn]* )
	    DEBUG "Skipping vim installation";
	    break;;
    esac
done

while true; do
    read -p "Do you wish to install emacs [y/N]? " ans
    case $ans in
	[Yy]* ) sudo yum install -y emacs;
		INFO "Installing emacs";
		
		# provide emacs shortcut to bashrc file
		while true; do
		    read -p "Would you like to add -nw option for emacs to bashrc [y/N]? " emans
		    case $emans in
			[Yy]* )
			    INFO "Adding emacs shortcut to bashrc"
			    echo "alias emacs='emacs -nw'" >> $BASHRC; break;;
			"" ) ;&  # fall through
			[Nn]* ) break;;
		    esac
		done
		break;;
	"" ) ;&  # fallthrough
	[Nn]* )
	    DEBUG "Skipping emacs installation";
	    break;;
    esac
done

		
# Add other shortcuts to the bashrc file
INFO "Adding other shortcuts to the bashrc file";

echo "# Command to remove all temp files created by emacs." >> $BASHRC;
echo "alias clean='rm -rf *~'" >> $BASHRC;


# Generate an RSA key
# Note: only a single key is generated, please execute on your own if you desire more
INFO "Generating an SSH key(s)."
DEBUG "Please follow the text carefully to ensure that your information is correct."

while true; do
    read -p "Would you like to generate a[nother] key [Y/n]? " cans
    case $cans in
	"" ) ;&
	[Nn]* ) break;;
	[Yy]* )
	    read -p "Does your system support the Ed25519 algorithm [y/N]? " ans
	    case $ans in
		[Yy]* ) ssh-keygen -t ed25519;;
		"" ) ;&
		[Nn]* ) ssh-keygen -t rsa -b 4096;;
	    esac
	    ;;
    esac
done

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

while true; do
    read -p "Would you like to generate a[nother] gpg-key [y/N]? " cans
    case $cans in
        "" ) ;&
        [Nn]* ) break;;
	[Yy]* )
	    DEBUG "Generating GPG Key, follow the instructions carefully."
	    if [ $UPDATED_GPG -eq 1 ]; then
		WARN "Use 4096 for the size or the key cannot be used."
		gpg --full-generate-key;
	    else
		gpg --default-new-key-algo rsa4096 --gen-key;
	    fi
	    ;;
	esac
done


read -p "Would you like to generate public gpg files [y/N]? " ans
case $ans in
    [Yy]* )
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

	;; # end generation
esac



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

INFO "Creating and Adding Keyboard shortcuts";
DEBUG "Keyboard shortcuts take a bit to load, adding to the bash profile";
