#!/bin/bash
# How to setup GeoDjango on AWS EB
# Created by Ryan G on 12-08-2016
#
# Updated 10-05-2017
# Latest "stock" beanstalk AMI for python2.7 == (aws-elasticbeanstalk-amzn-2017.03.1.x86_64-python27-hvm-201709251940 - ami-eb00f791)
#
# Background info / AWS instructions here: http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.customenv.html
#
# So you want GeoDjango to run on AWS Beanstalk Python 2.7? Two main steps:
# 1) Launch a base AMI, SSH into the EC2 instance and install these packages, save as custom image. You'll get a custom AMI ID.
# 2) Create an .ebextensions for the container_command (more info below, see file below) which will take the compiled GDAL python bindings and install to the virtual env
# 3) Create an .ebextensions called `django.config` to tell it to launch with your custom AMI.
#
#

sudo yum-config-manager --enable epel
sudo yum repolist

sudo yum -y install gcc gcc-c++ make cmake libtool libcurl-devel libxml2-devel rubygems swig fcgi-devel\
                    libtiff-devel freetype-devel curl-devel libpng-devel giflib-devel libjpeg-devel\
                    cairo-devel freetype-devel readline-devel openssl-devel
sudo yum -y group install "Development Tools"

wget http://download.osgeo.org/geos/geos-3.5.1.tar.bz2
tar xjf geos-3.5.1.tar.bz2
cd geos-3.5.1
./configure
make
sudo make install
cd ..

wget http://download.osgeo.org/proj/proj-4.9.1.tar.gz
wget http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz
tar xzf proj-4.9.1.tar.gz
cd proj-4.9.1/nad
tar xzf ../../proj-datumgrid-1.5.tar.gz
cd ..
./configure
make
sudo make install
cd ..

wget http://download.osgeo.org/gdal/1.11.2/gdal-1.11.2.tar.gz
tar xzf gdal-1.11.2.tar.gz
cd gdal-1.11.2
./configure --with-python
make
sudo make install
cd swig & make & cd python
cd ..

#
# YOU MUST create an .ebextensions
# It will install the python binaries via the "virtual environment" python instance (/opt/python/run/venv/bin/python)
# if you don't do this, you'll get an error "osgeo" module not found
#
# 00-gdal.config
#container_commands:
#  setup_gdal:
#    command: cd /home/ec2-user/gdal-1.11.2/swig/python && /opt/python/run/venv/bin/python setup.py install

echo /usr/local/lib | sudo tee --append /etc/ld.so.conf
sudo ldconfig

sudo yum -y install postgresql95-devel
wget http://download.osgeo.org/postgis/source/postgis-2.3.0.tar.gz
tar zxvf postgis-2.3.0.tar.gz 
cd postgis-2.3.0
./configure --with-geosconfig=/usr/local/bin/geos-config --with-gdalconfig=/usr/local/bin/gdal-config
make
sudo make install
cd ..

sudo ldconfig
