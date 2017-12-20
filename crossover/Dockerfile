FROM centos:centos7
MAINTAINER Maria Zakhalyavko <mariya.zakhalyavko@raytheon.com>

# Include SSH so it can be set up in the future
RUN yum update -y && yum install -y curl wget openssh-server

# Install XPRA
RUN rpm --import https://winswitch.org/gpg.asc && \
    curl http://xpra.org/dists/CentOS/winswitch.repo > /etc/yum.repos.d/winswitch.repo && \
    yum install -y xpra

# Install Crossover
RUN yum install -y https://media.codeweavers.com/pub/crossover/cxlinux/demo/crossover-16.2.5-1.rpm && \
    yum install -y libpng.i686

# Replace the wineservers with ones that have instrumented logging
COPY wineserver32 /opt/cxoffice/bin/wineserver32
COPY wineserver64 /opt/cxoffice/bin/wineserver64

# Port for XPRA
EXPOSE 10000

# XPRA needs to write temp files into the home directory and should not run as root
RUN useradd --create-home virtue --groups xpra
USER virtue
RUN mkdir /home/virtue/.xpra

# Run crossover through XPRA
CMD set XDG_RUNTIME_DIR=/home/virtue/.xpra && \
    xpra start :100 --start-child=/opt/cxoffice/bin/cxsetup --bind-tcp=0.0.0.0:10000 --exit-with-children --log-file=crossover.log && \
    sleep infinity