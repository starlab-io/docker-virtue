FROM starlabio/ubuntu-base:1.2
MAINTAINER Kyle Stapp <kyle.stapp@starlab.io>

# Ensure 64 bit only
RUN sed -e 's:deb h:deb [arch=amd64] h:' -e 's:deb-src h:deb-src [arch=amd64] h:' -i /etc/apt/sources.list && \
    find /etc/apt/sources.list.d/ -type f -exec sed -e 's:deb h:deb [arch=amd64] h:' -i {} \;

#General Image Update
RUN	apt-get -qy install software-properties-common && \
	add-apt-repository universe && \
	apt-get -qy update

RUN     apt-get -qy install openssh-server

#Install Xpra/WinSwitch Repo
RUN curl https://winswitch.org/gpg.asc | apt-key add - && \
	echo "deb http://winswitch.org/ xenial main" > /etc/apt/sources.list.d/winswitch.list

#Install Xpra
RUN	apt-get -qy install xpra

#Debug Tools
RUN apt-get -qy install vim 

RUN mkdir /root/.ssh && \
	chmod 700 /root/.ssh

#COPY set-authorized-keys.sh /root/.ssh/authorized_keys
RUN apt-get -qy install liblz4-tool python-gtkglext1
RUN pip install --upgrade pip
RUN pip install numpy opencv-python

#configure around root .profile being wonky
RUN sed -i "s/mesg n || true/test -t 0 \&\& mesg n/" /root/.profile

#Install Sample App
RUN apt-get -qy install gedit

#Configure ssh to allow key based auth and grab key from env
COPY sshd_config /etc/ssh/
COPY *.sh /root/

#TBD Restrict SSH to only run the one xpra command

#Auto start command
CMD /root/kickoff.sh

