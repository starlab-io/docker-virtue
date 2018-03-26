#!/usr/bin/env python

import yaml, docker, sys, os

class ContainerConfig():
    _REPOSITORY = 'virtue'
    _DEFAULT_BUILD_PATH = 'app-containers'

    _containers = 'containers'
    _images = 'image_tags'
    _listen_port = 'listen_port'
    _args = 'args'
    _base_image = 'base_image_tag'
    _Dockerfile = 'Dockerfile'

    def __init__(self):
        self.data = {}

    def load(self, filename):
        with open(filename, 'r') as f:
            self.data = yaml.load(f)

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(yaml.dump(self.data))

    def get_image_from_tag(self, tag):
        return '%s:%s' % (self._REPOSITORY, tag)

    def get_tag_names(self):
        try:
            return self.data[self._images].keys()
        except KeyError:
            return None

    def get_base_image(self, image):
        try: 
            return self.data[self._images][image][self._base_image]
        except KeyError:
            return None

    def get_Dockerfile(self, image):
        try:
            return os.path.basename(self.data[self._images][image][self._Dockerfile])
        except KeyError:
            return 'Dockerfile.%s' % (image)
    
    def get_build_path(self, image):
        try:
            return os.path.dirname(self.data[self._images][image][self._Dockerfile])
        except KeyError:
            return self._DEFAULT_BUILD_PATH

def build_image(conf, docker_client, tag_name):
    docker_image_name = conf.get_image_from_tag(tag_name)
    #try:
    #    img = docker_client.images.get(docker_image_name)
    #except docker.errors.ImageNotFound:
    print("Building '%s'..." % (tag_name), end='', flush=True)
    base = conf.get_base_image(tag_name)
    if base is not None:
        build_image_if_not_exists(conf, docker_client, base)
    path = conf.get_build_path(tag_name)
    dockerfile = conf.get_Dockerfile(tag_name)
    img = docker_client.images.build(path=path, dockerfile=dockerfile, tag=docker_image_name)
    print("[OK]")
    return img


if __name__ == '__main__':
    conf = ContainerConfig()
    conf.load('VirtueDockerConf.yaml')

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
        images[tag_name] = build_image_if_not_exists(conf, docker_client, tag_name)

    for img in images:
        print(images[img])
