# Crossover-docker minimal

FROM ubuntu:xenial
MAINTAINER Maria Zakhalyavko

# openssh-server installed in hopes of setting up xpra with ssh later
RUN apt-get update -q -y && apt-get install \
    curl \
    wget \
    openssh-server \
    python-netifaces \
    liblz4-tool \
    apt-utils -q -y

# Install XPRA
RUN curl https://xpra.org/gpg.asc | apt-key add -
RUN echo 'deb http://xpra.org/ xenial main' > /etc/apt/sources.list.d/xpra.list && \
    apt-get install -q -y software-properties-common && \
    add-apt-repository universe && \
    apt-get update -q -y && \
    apt-get install -q -y xpra

# Install Crossover
# Official instructions for installing Crossover specify installing through gdebi
RUN wget https://media.codeweavers.com/pub/crossover/cxlinux/demo/crossover_16.2.5-1.deb && \
    dpkg --add-architecture i386 && \
    apt-get update -q -y && \
    apt-get install gdebi libnss-mdns:i386 -q -y && \
    gdebi -q --non-interactive crossover_16.2.5-1.deb

RUN apt-get install -qy python-pip && pip install --upgrade pip && pip install python-uinput

RUN apt-get install -qy dbus

# Port for XPRA
EXPOSE 10000

# XPRA needs to write temp files into the home directory and should not run as root
RUN useradd -ms /bin/bash -g xpra virtue
RUN bash -c "echo -e \"virtue\nvirtue\" | passwd virtue"
RUN usermod -a -G xpra,sudo,lpadmin virtue
RUN mkdir -p /run/user/1000 && chmod -R 777 /run/user
RUN mkdir /run/xpra && chgrp xpra /run/xpra && chmod 775 /run/xpra
RUN mkdir /home/virtue/.xpra && chown virtue:xpra /home/virtue/.xpra

COPY start.sh /root/start.sh
RUN chmod 755 /root/start.sh

# Run crossover through XPRA
CMD /root/start.sh
