#!/bin/sh
set -e
sudo yum install python3 -y
rm -f ./awscli-bundle.zip
rm -rf ./awscli-bundle
curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
unzip awscli-bundle.zip
sudo ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
grep -qxF 'export PATH=$PATH:/usr/local/aws/bin' ~/.zshrc || echo 'export PATH=$PATH:/usr/local/aws/bin'>> ~/.zshrc
rm -f ./awscli-bundle.zip
rm -rf ./awscli-bundle
