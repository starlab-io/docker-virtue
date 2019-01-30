#!/usr/bin/env python3

# Author: Stanislav Ponomarev <stanislav.ponomarev@raytheon.com>
# Copyright 2018 Raytheon BBN Technologies Corp.

import sys, docker, subprocess, argparse, os
from shutil import copyfile
from ContainerConfig import ContainerConfig


def start_container(conf, docker_client, args):
    ''' Operates only on containers defined in config yaml file.
        Tries to start an existing container. If not found, creates a new container
        from the image that should already exist on this machine. 
        Figures out proper container run config based on the config yaml file.'''
    for container in args.containers:

        if container not in conf.get_container_names():
            print("ERROR! %s is not described in %s. Please add its entry before starting it" % (container, conf._DEFAULT_CONFIG_FILE))
            return
        container_obj = None
        container_name = container
        if args.pull:
            print("Pulling %s's image from the repository..." % (container_name), end='', flush=True)
            docker_client.images.pull(conf.get_repository(), conf.get_container_image_tag(container_name))
            print("[OK]")

        try:
            container_obj = docker_client.containers.get(container_name)
        except docker.errors.NotFound:
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
            if apparmor_file:
                profile_name = 'docker_%s' % (container.replace('-', '_'))
                # unlike seccomp, apparmor has a parser that needs to run aside from docker.
                # the parser will take apparmor file with a profile definition and store it
                # in its own database. Docker then just references it by profile name.
                # we decided that apparmor profiles will be called 'docker-%s' % (container_name)
                # so the following structure makes sure that the apparmor file contains 
                # the properly named profile
                print("Ensuring that the AppArmor profile is enabled for %s" % (container))

                cmd = []
                if os.getuid() == 0:
                    cmd.append('sudo')
                cmd.extend(['apparmor_parser', '-r', '-W'])

                if type(apparmor_file) is list:
                    for file_entry in apparmor_file:
                        # call the parser to load this profile
                        wfilecmd = list(cmd)
                        wfilecmd.append(file_entry)
                        subprocess.check_call(wfilecmd)
                        if args.restart:
                            copyfile(file_entry, os.path.join('/etc/apparmor.d/', os.path.basename(file_entry)))
                else:
                    # The following `with` block opens apparmor file and looks for profile_name inside the file
                    # But for the cases of multiple apparmor files this logic is way more complicated. 
                    # For now I'm implementing this check only for a single file and not a list
                    with open(apparmor_file, 'r') as f:
                        for line in f:
                            if 'profile' in line:
                                if profile_name in line:
                                    print("Found profile match: '%s'" % line[:-1]) # remove /n from the line
                                else:
                                    print("WARNING: AppArmor profile name does not match '%s'. App armor will error!" % (profile_name))
                                break
                    # call the parser to load this profile
                    wfilecmd = list(cmd)
                    wfilecmd.append(apparmor_file)
                    subprocess.check_call(wfilecmd)
                    if args.restart:
                        copyfile(apparmor_file, os.path.join('/etc/apparmor.d/', os.path.basename(apparmor_file)))
                    
                print("NOTE: Apparmor files are re-read only on container creation. If you change the file content, please remove the container and this this script again")
                print("NOTE: Applying apparmor profile %s" % profile_name)
                security_opt.append('apparmor=%s' % (profile_name))
                
                if args.debug:
                    docker_cmd.extend(['--security-opt', '"apparmor=%s"' % (profile_name)])
                
            if seccomp_file is not None:
                with open(seccomp_file, 'r') as f:
                    print("NOTE: Applying seccomp file %s" % seccomp_file)
                    security_opt.append('seccomp=%s' % (f.read()))
                if args.debug:
                    docker_cmd.extend(['--security-opt', '"seccomp=%s"' % (seccomp_file)])

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
                'cap_add': 'NET_ADMIN',
            }

            if args.restart:
                docker_args['restart_policy'] = {"Name": "always"}
            
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
                if args.debug:
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
    for container in args.containers:
        if container not in conf.get_container_names():
            print("ERROR! %s is not described in %s." % (container, conf._DEFAULT_CONFIG_FILE))
            return
        print("Stopping container %s ..." % (container), end='', flush=True)
        container_obj = docker_client.containers.get(container)
        container_obj.stop()
        print("[OK]")

def save_container(conf, docker_client, args):
    ''' Operates only on containers defined in config yaml. Both containers should be already defined.
        calls docker commit container and saves it as output image'''
    container = args.containers[0]
    output = args.containers[1]
    if container not in conf.get_container_names():
        print("ERROR! Container %s is not described in %s. Can't save a non-virtue container" % (container, conf._DEFAULT_CONFIG_FILE))
        return
    container_name = container
    #if output not in conf.get_tag_names():
    #    print("ERROR! image tag %s is not described in %s. Please add its entry before saving." % (output, conf._DEFAULT_CONFIG_FILE))
    #    return
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

def pack_container(conf, args):
    archive_filename = 'container_pack.tar.gz'
    file_list = []
    file_list.append('run.py')
    file_list.append(conf._DEFAULT_CONFIG_FILE)
    file_list.append('ContainerConfig.py')
    for container in args.containers:
        apparmor = conf.get_apparmor_file(container)
        seccomp = conf.get_seccomp_file(container)
        if apparmor is not None:
            if type(apparmor) is list:
                file_list.extend(apparmor)
            else:
                file_list.append(apparmor)
        if seccomp is not None:
            file_list.append(seccomp)
    print("The following files are saved to %s" % (archive_filename))
    print('\n'.join(file_list))
    cmd = ['tar', 'czf', archive_filename]
    cmd.extend(file_list)
    subprocess.check_call(cmd)
    


if __name__ == '__main__':
    conf = ContainerConfig()
    parser = argparse.ArgumentParser(description='Manage Virtue Containers')
    parser.add_argument('-d', '--debug', action='store_true', help='On docker faliure, output a docker command for bash that can perform the same action that failed')
    parser.add_argument('-p', '--pull', action='store_true', help='Pull the image from the repository before starting it. Make sure docker is authorized ahead of time with `docker login`')
    parser.add_argument('-r', '--restart', action='store_true', help='Start the docker container with always restart restart policy')
    parser.add_argument('action', choices=['start', 'stop', 'save', 'pack', 'list'], help='start|stop|save a container or list known virtue containers. Or pack everything needed to start a container into a tarball')
    parser.add_argument('containers', nargs='+', help='Docker container name as specified in %s. Get available list with "list" command. if you are saving, specify 2 containers (source and destination)' % (conf._DEFAULT_CONFIG_FILE))

    args = parser.parse_args()
    docker_client = docker.from_env()
    conf.sanity_check()

    if args.action =='start':
        start_container(conf, docker_client, args)
    elif args.action == 'save':
        if len(args.containers) != 2:
            parser.print_help()
            sys.exit(1)
        save_container(conf, docker_client, args)
    elif args.action == 'stop':
        stop_container(conf, docker_client, args)
    elif args.action == 'list':
        print("The following containers are available:")
        print('\n'.join(conf.get_container_names()))
    elif args.action == 'pack':
        pack_container(conf, args)
    else:
        print("opt == '%s'" % (opt))
        print_usage_and_exit()


