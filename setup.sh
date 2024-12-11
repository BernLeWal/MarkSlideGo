#!/bin/bash
# Setup script for installing the required dependencies to run the MARP tool (https://www.marp.app)
# which are NoodeJS, Google-Chrome and MARP itself.
# Usage: ./setup.sh

# Install NodeJS
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.nvm/nvm.sh
nvm install --lts
nvm use --lts
npm --version

# Install MARP (on top of NodeJS)
npm install --save-dev @marp-team/marp-cli
npx --version

# Install Google-Chrome (required for the html-rendering)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt -y install ./google-chrome-stable_current_amd64.deb
google-chrome --version

# Make the provided shell scripts executable
chmod +x *.sh
