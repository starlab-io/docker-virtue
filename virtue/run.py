#!/usr/bin/env python

# Author: Stanislav Ponomarev <stanislav.ponomarev@raytheon.com>
# Raytheon BBN Technologies

import sys, docker, subprocess, argparse
from ContainerConfig import ContainerConfig


def start_container(conf, docker_client, args):
    ''' Operates only on containers defined in config yaml file.
        Tries to start an existing container. If not found, creates a new container
        from the image that should already exist on this machine. 
        Figures out proper container run config based on the config yaml file.'''
    container = args.container

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

        docker_cmd = []
        if args.debug:
            docker_cmd = ['docker', 'create', '--env', '"SSHPUBKEY=`cat \"%s\"`"' % (conf.get_ssh_authorized_keys()), '--name', container_name]
        
        security_opt = []
        if apparmor_file and seccomp_file:
            profile_name = 'docker-%s' % (container)
            print("Ensuring that the AppArmor profile is enabled for %s" % (container))
            with open(apparmor_file, 'r') as f:
                for line in f:
                    if 'profile' in line:
                        if profile_name in line:
                            print("Found profile match: '%s'" % line[:-1])
                        else:
                            print("WARNING: AppArmor profile name does not match '%s'. App armor will error!" % (profile_name))
                        break
                
            #subprocess.check_call(['sudo', 'apparmor_parser', '-r', '-W', apparmor_file])
            security_opt.append('apparmor=%s' % (profile_name))
            if args.debug:
                docker_cmd.extend(['--security-opt', '"apparmor=%s"' % (profile_name)])
                docker_cmd.extend(['--security-opt', '"seccomp=%s"' % (seccomp_file)])
            with open(seccomp_file, 'r') as f:
                security_opt.append('seccomp=%s' % (f.read()))
        # ports format: { inside_container: outside_container}
        ports = {conf.get_sshd_port(): conf.get_ssh_port(container)}
        if args.debug:
            # of course docker command ports are listed in reverse order than docker api...
            docker_cmd.extend(['-p', '%s:%s' % (str(conf.get_ssh_port(container)), str(conf.get_sshd_port()))])

            
        environment = {'SSHPUBKEY': ssh_public_key}

        docker_args = { 'ports': ports,
            'image': image,
            'environment': environment,
            'security_opt': security_opt,
            'name': container_name,
        }
        
        # add any extra args from the yaml file
        extra_args = conf.get_extra_docker_args(container)
        docker_args.update(extra_args)
        if args.debug:
            for key in extra_args:
                docker_cmd.append("--%s" % (key.replace('_', '-')))
                if type(extra_args[key]) is str:
                    docker_cmd.append('"%s"' % (extra_args[key]))
                else:
                    print("WARNING: can not reconstruct debug command due to extra arguments passed to the container")
                    docker_cmd.append(str(type(extra_args[key])))
            docker_cmd.append(image)

        try:
            print("Creating docker container...", end='', flush=True)
            container_obj = docker_client.containers.create(**docker_args)
            print("[OK]")
        except docker.errors.APIError as e:
            print(e)
            if debug:
                print('\nError occoured while running command:')
                print(' '.join(docker_cmd))

            if container_obj is not None:
                container_obj.remove()
    
    try:
        print("Starting service %s ..." % (container), end='', flush=True)
        container_obj.start()
        print("[OK]")
    except docker.errors.APIError as e:
        print(e)


def stop_container(conf, docker_client, args):
    ''' Operates only on containers defined in config yaml.
        Stops a container '''
    container = args.container
    if container not in conf.get_container_names():
        print("ERROR! %s is not described in %s." % (container, conf._DEFAULT_CONFIG_FILE))
        return
    container_obj = docker_client.containers.get(container)
    container_obj.stop()

def save_container(conf, docker_client, args):
    ''' Operates only on containers defined in config yaml. Both containers should be already defined.
        calls docker commit container and saves it as output image'''
    container = args.container
    output = args.output
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
    parser.add_argument('action', choices=['start', 'stop', 'save', 'list'], help='start|stop|save a container or list known virtue containers')
    parser.add_argument('container', nargs='?', help='Docker container name as specified in %s. Get available list with "list" command.' % (conf._DEFAULT_CONFIG_FILE))
    parser.add_argument('output', metavar='save_destination', nargs='?', default=None, help='Destination container for save command')
    parser.add_argument('-d', '--debug', action='store_true', help='On docker faliure, output a docker command for bash that can perform the same action that failed')

    args = parser.parse_args()
    docker_client = docker.from_env()
    conf.sanity_check()

    if args.action =='start':
        start_container(conf, docker_client, args)
    elif args.action == 'save':
        if args.output is None:
            parser.print_help()
            sys.exit(1)
        save_container(conf, docker_client, args)
    elif args.action == 'stop':
        stop_container(conf, docker_client, args)
    elif args.action == 'list':
        print("The following containers are available:")
        print('\n'.join(conf.get_container_names()))
    else:
        print("opt == '%s'" % (opt))
        print_usage_and_exit()


