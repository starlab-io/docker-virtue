#!/usr/bin/env python

import sys, docker, subprocess, argparse
from ContainerConfig import ContainerConfig


def start_container(conf, docker_client, container):
    container_obj = None
    container_name = 'virtue_%s' % (container)
    try:
        container_obj = docker_client.containers.get(container_name)
        print("Starting existing container")
    except docker.errors.NotFound:
        print("Creating new container from image")
        image = conf.get_container_image(container)
        apparmor_file = conf.get_apparmor_file(container)
        seccomp_file = conf.get_seccomp_file(container)
        ssh_public_key = ""

        with open('/home/virtue/.ssh/authorized_keys', 'r') as f:
            ssh_public_key = f.read()
        
        security_opt = []
        if apparmor_file and seccomp_file:
            print("Ensuring that the AppArmor profile is enabled for %s" % (container))
            subprocess.check_call(['sudo', 'apparmor_parser', '-r', '-W', apparmor_file])
            security_opt.append('apparmor=docker-%s' % (container))
            with open(seccomp_file, 'r') as f:
                security_opt.append('seccomp=%s' % (f.read()))
        ports = {conf.get_listen_port(container): 2022}
        environment = {'SSHPUBKEY': ssh_public_key}

        docker_args = { 'ports': {conf.get_listen_port(container): 2022},
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
    container_obj = docker_client.containers.get('virtue_%s' % (container))
    container_obj.stop()

def save_container(conf, docker_client, container, output):
    container_name = 'virtue_%s' % (container)
    if not output.startswith('virtue'):
        output = 'virtue-%s' % (output)
    container_obj = None
    try:
        container_obj = docker_client.containers.get(container_name)
    except docker.errors.NotFound:
        print("ERROR: Container %s is not found")
        return

    repo = conf.get_repository()
    container_obj.commit(repository=repo, tag=output)
    print("New image '%s' is saved" % (output))
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control Virtue Containers')
    parser.add_argument('action', choices=['start', 'stop', 'save'], help='start|stop|save a container')
    parser.add_argument('container', help='docker container name')
    parser.add_argument('output', metavar='save_destination', nargs='?', default=None, help='Destination container for save command')

    args = parser.parse_args()
    conf = ContainerConfig()
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


