#!/bin/bash

if [ -f .zshrc ]; then
   echo "Sourcing zshrc";
   source /root/.zshrc;
fi

# start the z-shell
zsh
