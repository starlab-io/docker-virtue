docker-xen
===========

Usage:

The plan is ultimate to allow AWS to pushe sshkey credentials into the VM via 
the environment variables. For now, simply use local environment variables.

Export your public keys for any machine in SSHPUBKEY.  Then run:

```
docker run -it --rm -p 6767:22 -e SSHPUBKEY -v ~/docker-virtue/:/source virtue:virtuehost ./kickoff.sh
```
