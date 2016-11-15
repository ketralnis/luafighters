#!/bin/bash

# bootstrapper for Vagrant

set -ev

# we get node from here
add-apt-repository --yes ppa:chris-lea/node.js

apt-get update

USE_LUA_LIB="liblua5.2-dev liblua5.2-0-dbg"

#lua_sandox can use luajit but it needs some extra config stuff
#USE_LUA_LIB="libluajit-5.1-dev"

# the basics required to get lua_sandbox compiling
apt-get -y install python python-pip python-dev $USE_LUA_LIB

apt-get install -y \
    redis-server \
    daemontools \
    git

# python libraries are all installed via setup.py

# node stuff we need (see package.json that does most of it)
apt-get install -y \
    nodejs

# development conveniences
# apt-get -y install gdb python-all-dbg
# pip install pympler

cd /home/vagrant/luafighters

./setup.py develop

# build our JS
sudo -EHu vagrant make installjs

# make sure stuff seems to work before we go installing it
python -m luafighters.tests.tests

cat >/etc/init/luafighters-server.conf<<EOF
start on runlevel [2345]
stop on runlevel [016]
respawn
chdir /home/vagrant/luafighters
exec setuidgid vagrant make devserver
EOF

# requires redis to be up, which comes up by default
service luafighters-server start

cat >/etc/init/luafighters-watchify.conf<<EOF
start on runlevel [2345]
stop on runlevel [016]
respawn
chdir /home/vagrant/luafighters
exec setuidgid vagrant make watchjs
EOF

service luafighters-watchify start

sleep 1
tail /var/log/upstart/luafighters-*.log
