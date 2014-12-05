#! /usr/bin/env bash

apt-get update
apt-get install -y python-pip python-dev

pip install -r /vagrant/requirements.txt
