docker-xen
===========

Usage:

The plan is ultimate to allow AWS to pushe sshkey credentials into the VM via
the environment variables. For now, simply use local environment variables.

Export your public keys for any machine in SSHPUBKEY.  Then run:

```
docker run -it --rm -p 6767:22 -e SSHPUBKEY -v ~/docker-virtue/:/source virtue:virtuehost ./kickoff.sh
```

Build
=====

Build all of the containers by running:

```
./build
```

Start the Containers
====================

Start all of the containers by running:

```
./virtue start
```

This will expose the GEdit ssh session on port 6767 and the Firefox ssh session on port 6768.
For both of those, you can set up the tunnel by doing the following:

```
# Get to GEdit
ssh -N -p 6767 -L 2023:localhost:2023 virtue@<hostname>
# Get to Firefox
ssh -N -p 6768 -L 2024:localhost:2023 virtue@<hostname>
```

This will stop the containers:
```
./virtue stop
```
