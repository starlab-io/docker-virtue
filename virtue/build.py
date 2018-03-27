#!/usr/bin/env python

import docker, sys, os
from ContainerConfig import ContainerConfig


def build_image(conf, docker_client, tag_name):
    docker_image_name = conf.get_image_from_tag(tag_name)
    #try:
    #    img = docker_client.images.get(docker_image_name)
    #except docker.errors.ImageNotFound:
    base = conf.get_base_image(tag_name)
    if base is not None:
        build_image(conf, docker_client, base)
    path = conf.get_build_path(tag_name)
    dockerfile = conf.get_Dockerfile(tag_name)
    print("Building %s as %s" % (os.path.join(path, dockerfile), docker_image_name))
    img = docker_client.images.build(path=path, dockerfile=dockerfile, tag=docker_image_name)
    print("%s is built." % (tag_name))
    return img


if __name__ == '__main__':
    conf = ContainerConfig()

    toBuild = []
    
    if len(sys.argv) == 1:
        print("Building all of the containers...")
        toBuild.extend(conf.get_tag_names())
    else:
        iname = sys.argv[1]
        toBuild.append(iname)
        print("Building %s..." % (iname))

    docker_client = docker.from_env()

    images = {}
    for tag_name in toBuild:
        images[tag_name] = build_image(conf, docker_client, tag_name)

    for img in images:
        print(images[img])
