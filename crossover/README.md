# Building: 

1. `$ docker build -t crossover .`
- NOTE: The wineserver* files are the modified wine servers that Crossover relies on.  These have been instrumented with logging.
- NOTE: The docker build takes a while to run (xpra and crossover take a while to install).

# Running:

1. `$ sudo touch /var/log/crossover.log && sudo chmod 777 /var/log/crossover.log`
2. `$ docker-compose up -d`

OR

1. `$ touch crossover.log`
2. ``$ docker run -ti -p "10000:10000" -u virtue -v `pwd`/crossover.log:/home/virtue/.xpra/crossover.log crossover``

# Interacting:

1. Unless you're running the Docker container locally, make sure you are SSHed with X11 forwarding enabled.  
2. Find out the IP address of the docker container (`docker inspect <name of container> | grep IPAddress`)
3. `$ xpra attach tcp:172.18.0.2:10000  # replace with correct IP address`
- NOTE: Make sure you have the right IP address!  If you don't, xpra will seem like it's trying to start up but will time out.
- NOTE: Also, xpra sometimes takes a couple seconds to initialize.  So sometimes a connection timeout just means try again.
- TODO: Change xpra to use SSH for better security.  The problem right now is that sshd needs to be started as root while xpra should be run as a non-root user.  This makes running it in docker difficult.  Since we are not going to be actually using Docker in the final product, it should be possible to set it up properly, with ssh.
4. A Crossover window will pop up.  Click the "Show Bottles" button, then click Add and create a new Bottle.  
- IMPORTANT: When choosing an OS, pick a 64-bit Windows.  There are problems with the 32-bit systems on the current image.
5. In the left sidebar, click on the Bottle you just created.  This will show options in the right-hand panel.  Click on the "Run Command..." option.  (Alternatively, go to the Bottle menu and click "Run Command..." there.)  
6. Click Browse and select notepad.exe (`/home/virtue/.cxoffice/New_Bottle/dosdevices/c:/windows/notepad.exe`).  
7. Click Run, then select "Try Now" when Crossover asks about its license.

