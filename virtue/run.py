#!/usr/bin/env python

import sys, docker, subprocess, argparse
from ContainerConfig import ContainerConfig


def start_container(conf, docker_client, container):
    ''' Operates only on containers defined in config yaml file.
        Tries to start an existing container. If not found, creates a new container
        from the image that should already exist on this machine. 
        Figures out proper container run config based on the config yaml file.'''
    if container not in conf.get_container_names():
        print("ERROR! %s is not described in %s. Please add its entry before starting it" % (container, conf._DEFAULT_CONFIG_FILE))
        return
    container_obj = None
    container_name = container
    try:
        container_obj = docker_client.containers.get(container_name)
        print("Starting existing container")
    except docker.errors.NotFound:
        print("Creating new container from image")
        image = conf.get_container_image(container)
        apparmor_file = conf.get_apparmor_file(container)
        seccomp_file = conf.get_seccomp_file(container)
        ssh_public_key = ""

        with open(conf.get_ssh_authorized_keys(), 'r') as f:
           ssh_public_key = f.read()
        
        security_opt = []
        if apparmor_file and seccomp_file:
            print("Ensuring that the AppArmor profile is enabled for %s" % (container))
            subprocess.check_call(['sudo', 'apparmor_parser', '-r', '-W', apparmor_file])
            security_opt.append('apparmor=docker-%s' % (container))
            with open(seccomp_file, 'r') as f:
                security_opt.append('seccomp=%s' % (f.read()))
        # ports format: { inside_container: outside_container}
        ports = {conf.get_sshd_port(): conf.get_ssh_port(container)}
        environment = {'SSHPUBKEY': ssh_public_key}

        docker_args = { 'ports': ports,
            'image': image,
            'environment': environment,
            'security_opt': security_opt,
            'name': container_name,
        }
        
        # add any extra args from the yaml file
        docker_args.update(conf.get_extra_docker_args(container))
        try:
            container_obj = docker_client.containers.create(**docker_args)
        except docker.errors.APIError as e:
            print(e)
            if container_obj is not None:
                container_obj.remove()
        
    print("Starting service %s" % (container))
    container_obj.start()


def stop_container(conf, docker_client, container):
    ''' Operates only on containers defined in config yaml.
        Stops a container '''
    if container not in conf.get_container_names():
        print("ERROR! %s is not described in %s." % (container, conf._DEFAULT_CONFIG_FILE))
        return
    container_obj = docker_client.containers.get(container)
    container_obj.stop()

def save_container(conf, docker_client, container, output):
    ''' Operates only on containers defined in config yaml. Both containers should be already defined.
        calls docker commit container and saves it as output image'''
    if container not in conf.get_container_names():
        print("ERROR! Container %s is not described in %s. Can't save a non-virtue container" % (container, conf._DEFAULT_CONFIG_FILE))
        return
    container_name = container
    if output not in conf.get_tag_names():
        print("ERROR! image tag %s is not described in %s. Please add its entry before saving." % (output, conf._DEFAULT_CONFIG_FILE))
        return
    container_obj = None
    try:
        container_obj = docker_client.containers.get(container_name)
    except docker.errors.NotFound:
        print("ERROR: Container %s is not found")
        return

    repo = conf.get_repository()
    if container_obj.status == 'running':
        print("Container %s is still running. Stopping it..." % (container_name), end='', flush=True)
        container_obj.stop()
        print("[OK]")
        
    container_obj.commit(repository=repo, tag=output)
    print("New image '%s' is saved" % (output))
    


if __name__ == '__main__':
    conf = ContainerConfig()
    parser = argparse.ArgumentParser(description='Manage Virtue Containers')
    parser.add_argument('action', choices=['start', 'stop', 'save'], help='start|stop|save a container')
    parser.add_argument('container', help='Docker container name as specified in %s.' % (conf._DEFAULT_CONFIG_FILE))
    parser.add_argument('output', metavar='save_destination', nargs='?', default=None, help='Destination container for save command')

    args = parser.parse_args()
    docker_client = docker.from_env()

    if args.action =='start':
        start_container(conf, docker_client, args.container)
    elif args.action == 'save':
        if args.output is None:
            parser.print_help()
            sys.exit(1)
        save_container(conf, docker_client, args.container, args.output)
    elif args.action == 'stop':
        stop_container(conf, docker_client, args.container)
    else:
        print("opt == '%s'" % (opt))
        print_usage_and_exit()


