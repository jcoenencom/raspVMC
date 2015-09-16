#!/bin/bash
echo first of all update all packages on the pi
sudo apt-get update
sudo apt-get upgrade

echo Check apache2 instalation

if ( ! dpkg -s apache2 2> /dev/null | grep Status ); then
	echo apache2 not install proceeding with installation
	sudo apt-get install apache2 apache2-utils libapache2-mod-php5 php5
fi

echo check if socat is installed
if ( ! dpkg -s socat 2> /dev/null | grep Status); then
        echo socat not installed, installing it
        sudo apt-get install socat
fi


if ( ! dpkg -s python-serial 2> /dev/null | grep Status); then
echo python serial not installed, installing it
sudo apt-get install python-serial
fi

echo check if fhem is installed
if ( dpkg -s fhem 2> /dev/null | grep Status); then
	echo FHEM is already installed
else
   while [ "$OK" != "1" ]; do
	echo FHEM is not installed do you want it to be installed "(Y/N)" ?
	read -n 1 INST
	if [ "$INST" = "Y" ]; then
		echo " installing it"
		echo Installation of FHEM, getting certificate
		wget --no-check-certificate -qO - https://debian.fhem.de/archive.key | sudo apt-key add -
		if (! grep -q fhem /etc/apt/sources.list ); then
			echo add source in apt source file
			echo "deb https://debian.fhem.de/stable ./" | sudo tee -a /etc/apt/sources.list
		fi
		sudo apt-get update
		echo Check if apt-transport-https is installed
		if ( ! dpkg -s apt-transport-https 2> /dev/null | grep Status ); then
			echo add https transport
			sudo apt-get install apt-transport-https
		fi
		sudo sh -c '(echo "Acquire::https::debian.fhem.de::Verify-Peer \"false\";") > /etc/apt/apt.conf.d/30nohttps'
		echo installing fhem package
		sudo apt-get install fhem
		echo patching fhem config file for VMC
		OK="1"
	elif [ "$INST" != "N" ]; then
		echo " reply Y or N please"
	else
		OK="1"
	fi
   done
fi
echo configuring the station in VMC.ini.new
./config.py

echo installing configuration files 

if [ ! -d "/etc/VMC" ]; then
  sudo mkdir /etc/VMC
fi

if [ -e "/etc/VMC/VMC.ini" ]; then
  echo save old VMC.ini to /etc/VMC/VMC.ini.old
  sudo mv /etc/VMC/VMC.ini /etc/VMC/VMC.ini.old
fi
sudo cp VMC.ini.new /etc/VMC/VMC.ini

if [ -e /opt/fhem/fhem.cfg ]; then
#file exist check if VMC already defined (normally should be adapted with device as stated in config run)
	if [! grep VMC /opt/fhem/fhem.cfg ]; then
		sudo cat fhem.cfg >> /opt/fhem/fhem.cfg
	fi
fi
echo patching inittab automatic restart in case of crash
if (! grep -q server.py /etc/inittab ); then
        echo "vm:2345:respawn:/home/pi/raspVMC-master/server.py >>/var/log/VMCerr.log 2>&1" | sudo tee -a /etc/inittab
else
        sudo sed -i '/server.py/ c\vm:2345:respawn:\/home\/pi\/raspVMC-master\/server.py >>\/var\/log\/VMCerr.log 2>\&1/' /etc/inittab
fi
echo activating the server
sudo init q

echo installing web pages cgi and VMC library
sudo cp VMC?.html /var/www
sudo cp *.cgi /usr/lib/cgi-bin
sudo cp VMC.pyc /usr/lib/pymodules/python2.7/VMC.pyc
echo cleanup
rm raspVMC.zip
exit
