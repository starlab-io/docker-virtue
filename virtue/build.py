#!/usr/bin/env python

# Author: Stanislav Ponomarev <stanislav.ponomarev@raytheon.com>
# Raytheon BBN Technologies

import docker, sys, os, argparse
from ContainerConfig import ContainerConfig


def build_image(conf, docker_client, tag_name):
    ''' Only operates on image tags described in config yaml.
        If a specified image tag depends on another virtue image, builds that 
        image first. Then builds this image. '''
    if tag_name not in conf.get_tag_names():
        print("ERROR! image tag %s is not described in %s. Make sure you're trying to build a proper virtue image" % (tag_name, conf._DEFAULT_CONFIG_FILE))
        return
    docker_image_name = conf.get_image_from_tag(tag_name)
    # Check if this image depends on other virtue-image
    base = conf.get_base_image(tag_name)
    if base is not None:
        # if it does depend - build the dependency first
        build_image(conf, docker_client, base)
    path = conf.get_build_path(tag_name)
    dockerfile = conf.get_Dockerfile(tag_name)
    print("Building %s as %s ... " % (os.path.join(path, dockerfile), docker_image_name), end='', flush=True)
    try:
        img = docker_client.images.build(path=path, dockerfile=dockerfile, tag=docker_image_name)
    except docker.errors.BuildError as e:
        print("A build error has happened!")
        print(e)
        cmd = 'docker build -t %s -f %s %s' % (docker_image_name, os.path.join(path, dockerfile), path)
        print("Likely, something is wrong with the Dockerfile. Please run\n\t%s\nFor a more verbose error" % (cmd))
        return None
        
    print('[OK]')
    return img


if __name__ == '__main__':
    conf = ContainerConfig()
    parser = argparse.ArgumentParser(description='Build Virtue Images')
    parser.add_argument('-l', '--list', required=False, help='List available images instead of building them', action='store_true')
    parser.add_argument('-p', '--push', required=False, help='Push the image to the repository after building it. Make sure docker is authorized ahead of time with `docker login`.', action='store_true')
    parser.add_argument('image', nargs='?', default=None, help='Virtue Image to be built. Accepts only tags listed in %s. If unspecified, builds all of them.' % (conf._DEFAULT_CONFIG_FILE))
    args = parser.parse_args()

    conf.sanity_check()
    if args.list:
        print("The following images are available:")
        print('\n'.join(conf.get_tag_names()))
    else:
        toBuild = []
        
        if args.image is None:
            toBuild.extend(conf.get_tag_names())
        else:
            toBuild.append(args.image)

        docker_client = docker.from_env()

        images = {}
        for tag_name in toBuild:
            images[tag_name] = build_image(conf, docker_client, tag_name)
            if args.push:
                print("Pushing %s to repository ..." % (tag_name), end='', flush=True)
                docker_client.images.push(conf.get_repository(), tag_name)
                print("[OK]")

        print("Finished.")
