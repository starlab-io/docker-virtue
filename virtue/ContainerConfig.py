# Author: Stanislav Ponomarev <stanislav.ponomarev@raytheon.com>
# Copyright 2018 Raytheon BBN Technologies Corp.

import yaml, os

class ContainerConfig():
    ''' This class is a logic wrapper for the underlying yaml file.
    aside from providing specific functions to access parts of the yaml file,
    this class also runs a sanity check on most of the fields and provides default
    values where applicable.
    '''
    _DEFAULT_BUILD_PATH = 'app-containers'
    _DEFAULT_CONFIG_FILE = 'VirtueDockerConf.yaml'

    # The following entries are just text mapping of fields in the yaml file
    _sshd_port = 'sshd_port'
    _ssh_authorized_keys = 'ssh_authorized_keys_file'

    _containers = 'containers'
    _images = 'image_tags'
    _image_tag = 'image_tag'
    _ssh_port = 'ssh_port'
    _args = 'args'
    _base_image = 'base_image_tag'
    _Dockerfile = 'Dockerfile'
    _apparmor = 'apparmor'
    _seccomp = 'seccomp'
    _None_value = 'None'
    _repository = 'repository'

    def __init__(self):
        self.load(self._DEFAULT_CONFIG_FILE)

    def sanity_check(self):
        ''' Runs some sanity check on the config file.
            - SSH authorized keys file doesn't exist
            - ssh port collisions
            - ssh using random ports
            - containers without image
            - containers with image tag that's not defined
            - containers' seccomp file doesn't exist
            - containers' apparmor file doesn't exist
            - image's Dockerfile doesn't exist
            - image's base image doesn't exist/isn't defined
        '''

        if not os.path.exists(self.get_ssh_authorized_keys()):
            print("WARNING: ssh authorized keys file %s doesn't exist" % (self.get_ssh_authorized_keys()))

        ssh_ports_used = []
        for app_name in self.get_container_names():
            # Warn about ssh port collisions
            try:
                cport = self.get_ssh_port(app_name)
                if cport in ssh_ports_used:
                    print("WARNING: Container %s uses an already-taken ssh port %s" % (app_name, cport))
                else:
                    if cport is not None:
                        ssh_ports_used.append(cport)
            # Warn about random ssh ports
            except KeyError:
                print("WARNING: Container %s has no ssh_port defined and it will be random" % (app_name))

            # Warn about containers without an image tag
            imgtag = None
            try:
                imgtag = self.data[self._containers][app_name][self._image_tag]
            except KeyError:
                print("WARNING: Container %s doesn't have a defined image tag. You will not be able to start new container" % (app_name))

            # Warn about containers with an undefined image tag
            if imgtag not in self.get_tag_names():
                print("WARNING: Container %s has an image tag %s that is not defined. You will not be able to build the image for this container. This is OK if the container is meant for an installer." % (app_name, imgtag))

            # Warn if seccomp file doesn't exist
            seccomp = self.get_seccomp_file(app_name)
            if seccomp is not None and not os.path.exists(seccomp):
                print("WARNING: Container %s is meant to use seccomp file %s which doesn't exist" % (app_name, seccomp))

            # Warn if apparmor file doesn't exist
            apparmor = self.get_apparmor_file(app_name)
            if apparmor is not None:
                iter_data = []
                if type(apparmor) is list:
                    iter_data = apparmor
                else:
                    iter_data = [apparmor]
                for apparmor_entry in iter_data:
                    if not os.path.exists(apparmor_entry):
                        print("WARNING: Container %s is meant to use apparmor file %s which doesn't exist" % (app_name, apparmor_entry))

        for img_tag in self.get_tag_names():
            dockerfile_path = os.path.join(self.get_build_path(img_tag), self.get_Dockerfile(img_tag))
            # Warn about non-existing Dockerfiles
            if not os.path.exists(dockerfile_path):
                print("WARNING: Image %s's Dockerfile (%s) doesn't exist" % (img_tag, dockerfile_path))
            # Warn about non-existing base images.
            # Will alwas complain about virtue-base, because it IS the base image
            if self.get_base_image(img_tag) not in self.get_tag_names():
                print("WARNING: Base image of %s doesn't exist" % (img_tag))




    def load(self, filename):
        ''' Load config from file '''
        with open(filename, 'r') as f:
            self.data = yaml.load(f)

    def save(self, filename):
        ''' Save config to file '''
        with open(filename, 'w') as f:
            f.write(yaml.dump(self.data))

    def override(self, key, value):
        self.data[key] = value
            
    def get_repository(self):
        ''' Get default repository name'''
        return self.data[self._repository]

    def get_ssh_authorized_keys(self):
        return self.data[self._ssh_authorized_keys]

    def get_sshd_port(self):
        ''' Get what port sshd inside the containers is listening on. Same for all containers'''
        return self.data[self._sshd_port]

    def get_image_from_tag(self, tag):
        ''' Adds repository name to tag '''
        return '%s:%s' % (self.get_repository(), tag)

    def get_tag_names(self):
        ''' List all known image tags '''
        return self.data[self._images].keys()

    def get_container_names(self):
        ''' List all known container names'''
        return self.data[self._containers].keys()

    def get_base_image(self, image):
        ''' Given an image tag, see if it depends on another known image tag'''
        try: 
            return self.data[self._images][image][self._base_image]
        except KeyError:
            return None

    def get_Dockerfile(self, image):
        ''' Find a Dockerfile basename (no path) given an image tag.
            For an image 'virtue-sampleimage' default filename is 
            Dockerfile.virtue-sampleimage
            '''
        try:
            return os.path.basename(self.data[self._images][image][self._Dockerfile])
        except KeyError:
            return 'Dockerfile.%s' % (image)
    
    def get_build_path(self, image):
        ''' Find a Dockerfile path (no filename) given an image tag.
            For an image 'virtue-sampleimage' default path is
            ./app-containers/'''
        try:
            return os.path.dirname(self.data[self._images][image][self._Dockerfile])
        except KeyError:
            return self._DEFAULT_BUILD_PATH

    def get_ssh_port(self, container_name):
        ''' Find docker listen port for sshd. Default None will cause docker to choose a random port'''
        try:
            return self.data[self._containers][container_name][self._ssh_port]
        except KeyError:
            return None

    def get_container_image(self, container_name):
        ''' Find full image reference (repo:tag) by container name'''
        return self.get_image_from_tag(self.get_container_image_tag(container_name))

    def get_container_image_tag(self, container_name):
        return self.data[self._containers][container_name][self._image_tag]

    def get_apparmor_file(self, container_name):
        ''' Get file path to an apparmor profile by a container name. 
            To disable apparmor, enter value 'None'. If no value is given, defaults to
            ./app-containers/apparmor/apparmor.virtue-app.profile for a 'virtue-app' contianer
            '''
        try:
            value = self.data[self._containers][container_name][self._apparmor]
            if value == self._None_value:
                return None
            else:
                return value
        except KeyError:
            return os.path.join(self._DEFAULT_BUILD_PATH, 'apparmor', 'apparmor.%s.profile' % (container_name))

    def get_seccomp_file(self, container_name):
        ''' Get file path to a seccomp profile by a container name. 
            To disable seccomp, enter value 'None'. If no value is given, defaults to
            ./app-containers/seccomp/seccomp.virtue-app.json for a 'virtue-app' contianer
            '''
        try:
            value = self.data[self._containers][container_name][self._seccomp]
            if value == self._None_value:
                return None
            else:
                return value
        except KeyError:
            return os.path.join(self._DEFAULT_BUILD_PATH, 'seccomp', 'seccomp.%s.json' % (container_name))

    def get_extra_docker_args(self, container_name):
        ''' Get any extra docker run args needed by a given container name'''
        try:
            return self.data[self._containers][container_name][self._args]
        except KeyError:
            return {}



