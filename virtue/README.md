docker-virtue
=============

Copyright 2017, 2018 Raytheon BBN Technologies Corp.

The docker containers that include the virtue applications must be created in a very specific manner. In general,
the containers host an `xpra` instance listening on port 2023 and an ssh daemon listening on port 2022. Additionally,
the ssh daemon gets its authorized keys from an environment variable passed in on SSHPUBKEY into the container. The ssh
daemon is running as the `virtue` user inside of the container, but it only allows logins from the virtue user, who has no shell
inside of the container. Since the user has no login in the container, all it really makes sense to do is to set up an ssh tunnel
to the `xpra` port in the container.

As an example, with the default provided containers, you can get at gedit and firefox from your machine like follows:

```
# Where <hostname> is hostname of a machine with docker installed and running one of the containers.
# If <hostname> is localhost make sure to change -L 6767 to something else otherwise it'll conflict with -p 6767
ssh -N -p 6767 -L 6767:localhost:2023 virtue@<hostname>
```
The port that we are connecting to is 6767 (gedit) or 6768 (firefox) on `<hostname>`. The `-N` parameter says to not issue a remote command, which
is good since we have disabled all logins anyway and means that this session is only good for configuring a tunnel. The `-L` parameter
sets up a tunnel from the local port 6767 (gedit) or 6768 (firefox) to the port inside of each container (remember, we are exposing
the `xpra` port on port 2023 inside of the container for all containers). I chose to reuse the port number for my local client to be the
same as the port that I am connecting to on the remote host.


Dependencies
------------

Together `./build.py` and `run.py` depend on [docker-py](https://github.com/docker/docker-py)

VirtueDockerConf.yaml
-------------

The Virtue.config file format is YAML (http://yaml.org/). The file already has some containers defined and comments for sample containers:
```
containers:
	gedit:
		image_tag: virtue-gedit
		ssh_port: 6767
	firefox:
		image_tag: virtue-firefox
		ssh_port: 6767

image_tags:
	virtue-base:
		Dockerfile: virtue-base/Dockerfile.virtuebase
	virtue-gedit:
		base_image_tag: virtue-base
	virtue-firefox:
		base_image_tag: virtue-base

```

Possible container fields:
```
containers:
	samplecontainer:
	    image_tag: virtue-sampleimage # image tag of this container, image name is virtue:virtue-simplecontainer
        ssh_port: 6767 # default: random. Used with docker run, docker listen port
        args: {shm_value: 1g, read_only: False, ...} # a dictionary of python variables as keys and their values to use for python create
        apparmor: path-to-apparmor-profile # default: app-containers/apparmor/apparmor.samplecontainer.profile
		seccomp: path-to-seccomp-config # default: app-containers/seccomp/seccomp.samplecontainer.json
```

Possible image tag fields:
```
images:
	virtue-sampleimage:
	    Dockerfile: path-to-dockerfile # relative to build.py, default app-containers/Dockerfile.virtue-sampleimage
	    base_image_tag: virtue-base # builds 'virtue-base' image before trying to build this image

```

Build
-----

You can build all of the containers currently defined by running:
```
./build.py
```

Or you can build individual images by passing it as an argument
```
./build.py virtue-gedit
```

Whenever images are being built, the script ensures that the images defined in `base_image_tag` are built first.

Start the Containers
--------------------

Before starting the remote containers, the `ssh_authorized_keys_file` field in the config file needs to point to a valid file. Its content will be passed to the docker container as `SSHPUBKEY` environment variable with an assumption that sshd inside that container will only allow these keys to log in.

To start a specific container run
```
./run.py start samplecontainer
```
This container should be already built and described in the config file.

Note that to run the Office Virtue or the PuTTY Virtue, you need to 
```
./run.py start office-prep
# Make sure private key complement of ssh_authorized_key_file is available to you. See VirtueDockerConf.yaml
ssh -i private_key -N -p 7000 -L 7001:localhost:2023 virtue@localhost
xpra attach tcp:localhost:7001
# Now use GUI to install office (or other windows apps)
# exit out of xpra
./run.py save office-prep office
```
We hope to remove this requirement in the future, but for now, the installation process is too difficult to automate.


Stopping the Containers
------------------------

This will stop the containers:
```
./run.py stop samplecontainer
```

Building New Crossover-based Virtues
------------------------

To create a new Virtue, you need to add a Dockerfile to the app-containers directory, and then create seccomp and apparmor profiles for the new application.

The biggest challenge for Crossover-based Virtues is that it's very difficult to install applications into Crossover in an automated fashion. We're working on a way to do it without requiring GUI interaction, but for now, them's the breaks.

To create a new Virtue, run the following commands:

- `export SSHPUBKEY=$(cat virtue-test-key.pub)` # to load the test key as your pubkey
- `./virtue start Virtue-cxsetup.config` # to launch a Crossover cxsetup bottle running on port 7000
- `ssh-add virtue-test-key` # to load up the sshkey
- `ssh -N -p 7000 -L 7001:localhost:2023 virtue@localhost` # to set up the SSH tunnel. If successful, this will have no terminal output.
- In a new terminal window: `xpra attach tcp:localhost:7001` to open the Crossover Setup window
- Install the software into a new bottle using the Crossover interface
- On the final installation screen, make sure to select "Advanced Installation Options" and copy the list of dependencies to be installed
- Export the PuTTY Bottle as a Bottle Archive
	- In the cxsetup window, click the picture of the bottles in the top left to list the app bottles Crossover knows about
	- Right click on the app bottle and select "Export Bottle to Archive"
	- Pick a file location you can remember (I suggest /home/virtue) and hit OK
	- This will take a few minutes
- Build a new Dockerfile that installs the prereqs (listed under "Advanced" when you install the app in Crossover), copies in the cxarchive file, and then decompresses it. See `Dockerfile.virtue-putty` for an example.
- Add your app to `Virtue.config`
- Run `./virtue build Virtue.config`


Updating Containers
------------------------

The easiest way to update the containers is to check in any changes to the galahad-wine and docker-virtue git repositories and run the Jenkins virtue-wine and docker-virtue jobs.

Jenkins will generate all of the images except for virtue-office-word and virtue-office-outlook because Office must be installed manually.  It is preferable to create these two images on a local machine rather than an EC2 container.  To create them:

- Log in to docker through AWS using `./get_docker_login_command.sh`
- Pull the virtue-office-prep image built by CI: `docker pull 703915126451.dkr.ecr.us-east-2.amazonaws.com/starlab-virtue-ci:virtue-office-prep`
- You will also need an ISO for Microsoft Office
    - Mount the MS Office ISO (or otherwise extract it to a directory)
    - In VirtueDockerConf.yaml, add a volume under office-prep that points to the mounted ISO location, for example the last line in:
```
    office-prep:
        image_tag: virtue-office-prep
        ssh_port: 6769
        apparmor: None # This is an install container. Should be used only to install a given application
        seccomp: None
        args:
            volumes:
             # Used to bring syslog messages from the container to the host's syslog-ng
             - /dev/log:/dev/log
             - /home/mariaz/msoffice2013:/home/virtue/msoffice2013
```
- You may also need to change the ssh_authorized_keys_file in VirtueDockerConf.yaml to a path that exists for you
- Start the container with: `./run.py start office-prep`
- Connect to the container either directly using XPRA or through Canvas.  You will need an SSH tunnel if connecting directly to XPRA.
- In a browser, go to `localhost:10000` (or whatever port you've forwarded to).  You will see the Crossover selection dialog.  It may be hidden in the bottom right corner.  Click "Install Windows Software" and select the directory where you've volumed in the ISO file.  Click through the rest of the installer.
- Back in your terminal, run `./run.py save office-prep office-word` and `./run.py save office-prep office-outlook`
- Tag the newly created images with the main repository:
```
docker tag <word image id> 703915126451.dkr.ecr.us-east-2.amazonaws.com/starlab-virtue:virtue-office-word
docker tag <word image id> 703915126451.dkr.ecr.us-east-2.amazonaws.com/starlab-virtue:virtue-office-outlook
```

Now that these two images are done, pull the rest of the containers from the CI repo and retag them to the main repo:
```
python3 publish.py -l -e office-word -e office-outlook
```

And then push all of the containers to the main repo:
```
python3 publish.py -s
```

