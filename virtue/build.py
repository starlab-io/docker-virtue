#!/usr/bin/env python3

# Author: Stanislav Ponomarev <stanislav.ponomarev@raytheon.com>
# Copyright 2018, Raytheon BBN Technologies Corp.

import docker, sys, os, argparse, json
from ContainerConfig import ContainerConfig


def build_image(conf, docker_client, tag_name, nocache=False):
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
        build_image(conf, docker_client, base, nocache)
    path = conf.get_build_path(tag_name)
    dockerfile = conf.get_Dockerfile(tag_name)
    print("Building %s as %s ... " % (os.path.join(path, dockerfile), docker_image_name), end='', flush=True)
    try:
        img = docker_client.images.build(path=path, dockerfile=dockerfile, \
            tag=docker_image_name, nocache=nocache)
    except docker.errors.BuildError as e:
        print("A build error has happened!")
        print(e)
        cmd = 'docker build -t %s -f %s %s %s' % (docker_image_name, \
            os.path.join(path, dockerfile), \
            '--no-cache' if nocache else '', \
            path)
        print("Likely, something is wrong with the Dockerfile. Please run\n\t%s\nFor a more verbose error" % (cmd))
        return None
        
    print('[OK]')
    return img


if __name__ == '__main__':
    conf = ContainerConfig()
    parser = argparse.ArgumentParser(description='Build Virtue Images')
    parser.add_argument('-l', '--list', required=False, help='List available images instead of building them', action='store_true')
    parser.add_argument('-p', '--push', required=False, help='Push the image to the repository after building it. Make sure docker is authorized ahead of time with `docker login`.', action='store_true')
    parser.add_argument('-r', '--repo', required=False, help='Override repo in config file')
    parser.add_argument('-o', '--imagefile', required=False, default=None, help='Write image URIs to file')
    parser.add_argument('-n', '--nocache', required=False, help='Rebuild every layer of the container from scratch', action='store_true')
    parser.add_argument('image', nargs='?', default=None, help='Virtue Image to be built. Accepts only tags listed in %s. If unspecified, builds all of them.' % (conf._DEFAULT_CONFIG_FILE))
    args = parser.parse_args()

    conf.sanity_check()
    if args.list:
        print("The following images are available:")
        print('\n'.join(conf.get_tag_names()))
    else:
        toBuild = []

        print('REPO from config: ' + conf.get_repository())
        if args.repo is not None:
            print('args.repo       : ' + args.repo)
            conf.override(conf._repository, args.repo)
        
        if args.image is None:
            toBuild.extend(conf.get_tag_names())
        else:
            toBuild.append(args.image)

        docker_client = docker.from_env()
        
            
        images = {}
        image_uris = {}
        for tag_name in toBuild:
            images[tag_name] = build_image(conf, docker_client, tag_name, args.nocache)
            if images[tag_name] is None:
                image_uris[tag_name] = None
            else:
                image_uris[tag_name] = conf.get_repository() + ":" + tag_name
            if args.push:
                if images[tag_name] is None:
                    print("Skipping %s - build failed" % tag_name)
                    continue
                print("Pushing %s to repository ..." % (tag_name), end='', flush=True)
                docker_client.images.push(conf.get_repository(), tag_name)
                print("[OK]")                   
        
        if args.imagefile:
            with open(args.imagefile, 'w') as outfile:
                json.dump(image_uris, outfile, indent=4, sort_keys=True) 

        print("Finished.")

        
