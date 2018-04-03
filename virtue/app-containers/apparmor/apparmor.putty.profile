# Last Modified: Tue Mar 27 16:29:23 2018
#include <tunables/global>

profile docker_putty flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/bash>
  #include <abstractions/consoles>
  

  /home/virtue/kickoff.sh         rmPx -> kickoff,

}

# ----------------------------------- Kickoff ------------------------------------

profile kickoff flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/bash>
  #include <abstractions/consoles>
  #include <abstractions/nameservice>
  #include <abstractions/python>

  /bin/bash rmix,
  /home/virtue/kickoff.sh r,
  /home/virtue/set-authorized-keys.sh rmix,

  # Helper stuff
  /bin/mkdir rmix,
  /bin/chmod rmix,

  /usr/bin/xpra     Px -> xpra,
  /usr/sbin/sshd    Px -> sshd,

  /home/virtue/.ssh/authorized_keys rw,

  /etc/ld.so.cache r,
  /lib/x86_64-linux-gnu/ld-*.so mr,
  /lib/x86_64-linux-gnu/* mr,    

  /home/virtue/.xpra/ rw,
}

# ------------------------------------ XPRA ------------------------------------

profile xpra flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/authentication>
  #include <abstractions/dbus>
  #include <abstractions/gnome>
  #include <abstractions/nameservice>
  #include <abstractions/python>

  ########################
  # Non-file stuff
  ########################
  network unix stream,
  signal (send) set=(term) peer=unconfined, # This seems... really dangerous?


  ########################
  # Python libraries - note this is relatively unconstrained...
  ########################
  # So when you use the Docker overlay2 storage driver, sometimes apparmor
  # comes up with the container-internal path, sometimes it comes up with the
  # overlay2/<sha1>/diff path. I cannot determine how to get around this, so
  # we use the {} notation to specify a set of options
  /usr/bin/python2.7 rm,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python{2.[4-7],3.[0-5]}/**.{py,pyc,so}         mr,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python{2.[4-7],3.[0-5]}/**.{egg,py,pth}        r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python{2.[4-7],3.[0-5]}/{site,dist}-packages/  r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python{2.[4-7],3.[0-5]}/{site,dist}-packages/** r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python3.[0-5]/                                 r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python3.[0-5]/*/                               r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python3.[0-5]/lib-dynload/*.so                 mr,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python{2.[4-7],3.[0-5]}/**.{pyc,so}      mr,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python{2.[4-7],3.[0-5]}/**.{egg,py,pth}  r,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python{2.[4-7],3.[0-5]}/{site,dist}-packages/ r,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python{2.[4-7],3.[0-5]}/{site,dist}-packages/** r,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python3.[0-5]/lib-dynload/*.so           mr,
  /{,docker/overlay2/*/diff/}usr/lib/python3/dist-packages/                                 r,
  /{,docker/overlay2/*/diff/}usr/lib/python3/dist-packages/**.so                            mr,


  ########################
  # Core XPRA files
  ########################
  /usr/bin/xpra rmix,
  /{,docker/overlay2/*/diff/}etc/xpra/conf.d/ r,
  /{,docker/overlay2/*/diff/}etc/xpra/conf.d/** r,
  /home/virtue/.xpra/** rw,
  
  /home/virtue/.cache/ rw,
  /home/virtue/.cache/gstreamer-1.0/ rw,
  /home/virtue/.cache/gstreamer-1.0/** rw,

  /home/virtue/.dbus/ rw,
  /home/virtue/.dbus/session-bus/ rw,
  /home/virtue/.dbus/session-bus/** rw,

  /run/xpra/ rw,

  ########################
  # Devices & Interfaces
  ########################
  /sys/devices/virtual/misc/uinput/uevent r,
  /sys/module/apparmor/parameters/enabled r,


  ########################
  # Things in /proc
  ########################
  @{PROC}/@{pid}/cmdline r,
  @{PROC}/@{pid}/status r,
  @{PROC}/@{pid}/mounts r,
  @{PROC}/@{pid}/pid r,
  @{PROC}/@{pid}/fd/ r,


  ########################
  # Misc.
  ########################
  # Does not seem to be a way to restrict this further
  /tmp/** rw,
  /etc/lsb-release r,
  /etc/magic r,
  /etc/mime.types r,
  /usr/share/file/** r,
  /home/virtue/.Xauthority* lrw,


  ########################
  # DBUS
  ########################
  /var/lib/dbus/machine-id r,
  /etc/machine-id r,
  /usr/bin/dbus-launch rmix,
  /usr/bin/dbus-daemon rmix,
  /usr/share/dbus-*/session.conf r,
  /usr/share/dbus-*/session.d/** r,
  /docker/overlay2/*/diff/etc/dbus-*/session.d/ r,
  /etc/dbus-1/session.d/ r,
  /{,docker/overlay2/*/diff/}usr/share/dbus-1/services/ r,
  /{,docker/overlay2/*/diff/}usr/share/dbus-1/services/** r,
  /{,docker/overlay2/*/diff/}usr/share/dbus-1/system-services/ r,
  /{,docker/overlay2/*/diff/}usr/share/dbus-1/system-services/org.freedesktop.systemd1.service r,

  /{,docker/overlay2/*/diff/}usr/lib/x86_64-linux-gnu/girepository-1.0/ r,
  /{,docker/overlay2/*/diff/}usr/lib/girepository-1.0/ r,
  /{,docker/overlay2/*/diff/}usr/lib/x86_64-linux-gnu/gstreamer-1.0/ r,
  /{,docker/overlay2/*/diff/}usr/lib/x86_64-linux-gnu/gstreamer-1.0/gstreamer-1.0/gst-plugin-scanner rmix,
  /{,docker/overlay2/*/diff/}usr/lib/x86_64-linux-gnu/gstreamer1.0/ r,
  /{,docker/overlay2/*/diff/}usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-plugin-scanner rmix,
  /dev/ r,    

  /{,docker/overlay2/*/diff/}usr/lib/x86_64-linux-gnu/gio/modules/ r,



  ########################
  # Helper applications
  ########################
  /sbin/ldconfig rmix,
  /sbin/ldconfig.real rmix,
  /usr/bin/lsb_release rmUx,  # this guy does a bunch of *weird* stuff
  /usr/bin/xauth rmix,
  /bin/dash rmix,             # no separate profile
  /bin/uname rmix,
  /usr/bin/file rmix,
  /usr/sbin/lpinfo rmix,

  /usr/bin/Xvfb rmpx -> xpra_xvfb,

}

# ------------------------------------ Xvfb ------------------------------------

profile xpra_xvfb flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/fonts>
  #include <abstractions/X>

  network inet stream,
  network unix stream,

  /usr/bin/Xvfb rm,

  # I think this path is controlled by a config file somewhere,
  # or a command line argument. Caveat cursor!
  /home/virtue/.xpra/xpra/*.log rw,

  /tmp/** rw,


  @{PROC}/@{pid}/cmdline r,
  @{PROC}/@{pid}/status r,
  @{PROC}/@{pid}/mounts r,
  @{PROC}/@{pid}/pid r,
  @{PROC}/@{pid}/fd/ r,

  ########################
  # Helper applications
  ########################
  /bin/dash rmix,
  /usr/bin/xkbcomp rmix,

}

# ------------------------------------ sshd ------------------------------------

profile sshd flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/authentication>
  #include <abstractions/base>
  #include <abstractions/consoles>
  #include <abstractions/nameservice>
  #include <abstractions/wutmp>

  capability sys_chroot,
  capability sys_resource,
  capability sys_tty_config,
  capability net_bind_service,
  capability chown,
  capability fowner,
  capability kill,
  capability setgid,
  capability setuid,
  capability audit_control,
  capability audit_write,
  capability net_admin,
  capability dac_override,
  capability dac_read_search,
  capability sys_ptrace,

  # sshd doesn't require net_admin. libpam-systemd tries to
  # use it if available to set the send/receive buffers size,
  # but will fall back to a non-privileged version if it fails.
  deny capability net_admin,

  # needed when /proc is mounted with hidepid>=1
  ptrace (read,trace) peer="unconfined",

  /dev/ptmx rw,
  /dev/pts/[0-9]* rw,
  /dev/urandom r,
  /etc/default/locale r,
  /etc/environment r,
  /etc/hosts.allow r,
  /etc/hosts.deny r,
  /etc/modules.conf r,
  /etc/security/** r,
  /etc/ssh/** r,
  /etc/ssl/openssl.cnf r,
  /usr/sbin/sshd mrix,
  /var/log/btmp rw,
  owner /{,var/}run/sshd{,.init}.pid wl,
  owner /{,var/}run/systemd/notify w,
  @{HOME}/.ssh/authorized_keys{,2} r,

  @{PROC}/cmdline r,
  @{PROC}/1/environ r,
  @{PROC}/@{pids}/fd/ r,  # pid of the just-logged in user's shell
  owner @{PROC}/@{pid}/loginuid rw,
  owner @{PROC}/@{pid}/limits r,
  owner @{PROC}/@{pid}/uid_map r,
  owner @{PROC}/@{pid}/mounts r,
  owner @{PROC}/@{pid}/oom_adj rw,
  owner @{PROC}/@{pid}/oom_score_adj rw,

  /sys/fs/cgroup/*/user/*/[0-9]*/ rw,
  /sys/fs/cgroup/systemd/user.slice/user-[0-9]*.slice/session-c[0-9]*.scope/ rw,

  # should only be here for use in non-change-hat openssh
  # duplicated from EXEC hat (+r)
  /bin/bash     cix -> ssh_shell,
  /bin/dash     cix -> ssh_shell,
  /{,usr/}sbin/nologin Uxr,
  /bin/false    Uxr,

  /sbin/unix_chkpwd rmix,

  # duplicated from AUTHENTICATED
  /etc.legal r,
  /etc/motd r,
  /{,var/}run/motd{,.dynamic}{,.new} rw,
  /tmp/ssh-[a-zA-Z0-9]*/ w,
  /tmp/ssh-[a-zA-Z0-9]*/agent.[0-9]* wl,

  # for internal-sftp
  /         r,
  /**       r,
  owner /** rwl,

  /usr/lib/openssh/sftp-server PUx,

  # This is for shells launched by SSHD
  profile ssh_shell {
    #include <abstractions/consoles>
    #include <abstractions/bash>
    #include <abstractions/authentication>
  }

}