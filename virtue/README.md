docker-virtue
=============

The docker containers that include the virtue applications must be created in a very specific manner. In general,
the containers host an `xpra` instance listening on port 2023 and an ssh daemon listening on port 2022. Additionally,
the ssh daemon gets its authorized keys from an environment variable passed in on SSHPUBKEY into the container. The ssh
daemon is running as the `virtue` user inside of the container, but it only allows logins from the virtue user, who has no shell
inside of the container. Since the user has no login in the container, all it really makes sense to do is to set up an ssh tunnel
to the `xpra` port in the container.

As an example, with the default provided containers, you can get at gedit and firefox from your machine like follows:

```
# Get to gedit
ssh -N -p 6767 -L 6767:localhost:2023 virtue@<hostname>
# Get to firefox
ssh -N -p 6768 -L 6768:localhost:2023 virtue@<hostname>
```
The port that we are connecting to is 6767 (gedit) or 6768 (firefox) on `<hostname>`. The `-N` parameter says to not issue a remote command, which
is good since we have disabled all logins anyway and means that this session is only good for configuring a tunnel. The `-L` parameter
sets up a tunnel from the local port 6767 (gedit) or 6768 (firefox) to the port inside of each container (remember, we are exposing
the `xpra` port on port 2023 inside of the container for all containers). I chose to reuse the port number for my local client to be the
same as the port that I am connecting to on the remote host.

Virtue.config
-------------

The Virtue.config file format is a series of lines like the following:
```
gedit|6767|
firefox|6768|--shm-size=1g
```
or, more generally, each line is a '|' delimited string with `<name>|<port>|<additional docker args>`.
The `<name>` field is special. It is used to look up the name of the Dockerfile for the building step and is used to look up
the name of the container when starting or stopping virtues. For instance, the Dockerfiles for all of the virtue containers will
be named `Dockerfile.virtue-<name>`. Additionally, the seccomp profile must be present and named `seccomp.<name>.json` and an
AppArmor profile must be present and named `apparmor.<name>.profile`, with a profile inside of it named `docker-<name>`.

The `<port>` field must be present in the file since that is the port that the ssh daemon for the container is exposed on. These
ports must be unique to this particular VM (they cannot overlap).

The `<additional docker args>` are additional command line parameters that you want to pass to the docker container. For instance,
the firefox docker container must have an additional argument to expand the size of the shared memory available inside of the container.

Why a `Virtue.config` file in this format instead of simply using the `docker-compose.yml` file to get similar functionality? Basically,
Docker Compose doesn't have support for passing in the seccomp profile at the moment &mdash; it is an outstanding bug. Hence, this simple
script and config file to do something similar.

Build
-----

You can build all of the containers currently defined by running:
```
./virtue build (Virtue.config)
```
where you the Virtue.config file is optional (it will read from a file called Virtue.config by default, but you can pass your own).

Start the Containers
--------------------

Before starting the remote containers, the SSHPUBKEY environment variable needs to be set. A future enhancement could be to take this
in as a file or read it from some other location and setting it in the environment before actually starting the container, but it is
required that you have it set first.

Start all of the containers by running:
```
./virtue start (Virtue.config)
```
where you the Virtue.config file is optional (it will read from a file called Virtue.config by default, but you can pass your own).

Stopping the Containers
------------------------

This will stop the containers:
```
./virtue stop (Virtue.config)
```
where you the Virtue.config file is optional (it will read from a file called Virtue.config by default, but you can pass your own).



Building New Virtues
------------------------

To create a new Virtue, you need to add a Dockerfile to the app-containers directory, and then create seccomp and 
apparmor profiles for the new application. 