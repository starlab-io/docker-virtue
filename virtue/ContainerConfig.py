import yaml, os

class ContainerConfig():
    _REPOSITORY = 'virtue'
    _DEFAULT_BUILD_PATH = 'app-containers'
    _DEFAULT_CONFIG_FILE = 'VirtueDockerConf.yaml'

    _containers = 'containers'
    _images = 'image_tags'
    _image_tag = 'image_tag'
    _listen_port = 'listen_port'
    _args = 'args'
    _base_image = 'base_image_tag'
    _Dockerfile = 'Dockerfile'
    _apparmor = 'apparmor'
    _seccomp = 'seccomp'
    _None_value = 'None'

    def __init__(self):
        self.load(self._DEFAULT_CONFIG_FILE)

    def load(self, filename):
        with open(filename, 'r') as f:
            self.data = yaml.load(f)

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(yaml.dump(self.data))
    
    def get_repository(self):
        return self._REPOSITORY

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

    def get_listen_port(self, container_name):
        return self.data[self._containers][container_name][self._listen_port]

    def get_container_image(self, container_name):
        return self.get_image_from_tag(self.data[self._containers][container_name][self._image_tag])

    def get_apparmor_file(self, container_name):
        try:
            value = self.data[self._containers][container_name][self._apparmor]
            if value == self._None_value:
                return None
            else:
                return value
        except KeyError:
            return os.path.join(self._DEFAULT_BUILD_PATH, 'apparmor', 'apparmor.%s.profile' % (container_name))

    def get_seccomp_file(self, container_name):
        try:
            value = self.data[self._containers][container_name][self._seccomp]
            if value == self._None_value:
                return None
            else:
                return value
        except KeyError:
            return os.path.join(self._DEFAULT_BUILD_PATH, 'seccomp', 'seccomp.%s.json' % (container_name))

    def get_extra_docker_args(self, container_name):
        try:
            return self.data[self._containers][container_name][self._args]
        except KeyError:
            return {}



