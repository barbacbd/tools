#!/bin/bash

if [ -d /fonts ]; then
   echo "Installing fonts locally ...";
   cd fonts;
   ./install.sh;

   result=$?;
   cd ..;
   
   if [ $result -eq 0 ]; then
       echo "Removing fonts dir ...";
       rm -rf fonts;
   else
       echo "Failed to install fonts, keeping fonts project ...";
   fi  
fi


if [ ! -f /usr/local/share/zsh/site-functions/prompt_spaceship_setup ]; then
   echo "Creating the symlink for spaceship-prompt";
   ln -s /spaceship-prompt/spaceship.zsh /usr/local/share/zsh/site-functions/prompt_spaceship_setup
fi
