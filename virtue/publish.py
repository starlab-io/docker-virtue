#!/usr/bin/env python3

#
# This script is used for pulling all images from the CI ECS repo, tagging them as part of the
# main repo, and pushing them to the main repo.
# Note that the virtue-office-word and virtue-office-outlook containers need to be created manually,
# starting with the base virtue-office-prep image and installing MS Office on top.
#

import docker, argparse
from ContainerConfig import ContainerConfig

def pull_containers(docker_client, containers, old_repo):
    for container in containers:
        try:
            print("Pulling image for container " + container + "...")
            docker_client.images.pull(old_repo, conf.get_container_image_tag(container))
        except docker.errors.APIError as e:
            print("ERROR: Failed to pull image for container " + container + " because: " + str(e))

def tag_containers(docker_client, containers, old_repo, new_repo):
    for container in containers:
        try:
            print("Tagging image for container " + container + "...")
            image_name = conf.get_container_image_tag(container)
            image = docker_client.images.get(old_repo + ":" + image_name)

            image.tag(new_repo, image_name)
        except docker.errors.ImageNotFound as e:
            print("ERROR: Image not found for container " + container + ": " + str(e))
        except docker.errors.APIError as e:
            print("ERROR: Failed to tag image for container " + container + " because: " + str(e))

def push_containers(docker_client, containers, new_repo):
    for container in containers:
        try:
            print("Pushing image for container " + container + "...")
            image_name = conf.get_container_image_tag(container)
            for line in docker_client.images.push(new_repo, image_name, stream=True):
                print(line, end='\r')
        except docker.errors.APIError as e:
            print("ERROR: Failed to tag image for container " + container + " because: " + str(e))

if __name__ == '__main__':
    conf = ContainerConfig()
    parser = argparse.ArgumentParser(description='Update Virtue Containers')
    parser.add_argument('-o', '--old_repo', help='Address of old repository', default='703915126451.dkr.ecr.us-east-2.amazonaws.com/starlab-virtue-ci')
    parser.add_argument('-n', '--new_repo', help='Address of new repository', default='703915126451.dkr.ecr.us-east-2.amazonaws.com/starlab-virtue')
    parser.add_argument('-e', '--exclude', help='Container to exclude (may use multiple times)', action='append')
    parser.add_argument('-l', '--pull', help='Pull and tag only', action='store_true')
    parser.add_argument('-s', '--push', help='Push only', action='store_true')
    parser.add_argument('containers', nargs='*', help='Docker container names as specified in the yaml file.  Leave blank for all, and use -e if necessary.')

    args = parser.parse_args()
    docker_client = docker.from_env()
    conf.sanity_check()

    print("Make sure docker is authorized ahead of time with `docker login`") 

    containers = args.containers
    if len(args.containers) == 0:
        containers = list(conf.get_container_names())
    if args.exclude is not None:
        for c in args.exclude:
            containers.remove(c)

    print("Running pull/tag/push on the following images:")
    print('\n'.join(containers))

    if not args.push:
        pull_containers(docker_client, containers, args.old_repo)
        tag_containers(docker_client, containers, args.old_repo, args.new_repo)

    if not args.pull:
        push_containers(docker_client, containers, args.new_repo)
