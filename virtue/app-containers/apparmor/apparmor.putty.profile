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
  # Main application goes here!
  ########################
  /opt/cxoffice/bin/crossover rmpx -> crossover,


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
  /usr/bin/xpra rmpix -> xpra,
  /{,docker/overlay2/*/diff/}etc/xpra/conf.d/ r,
  /{,docker/overlay2/*/diff/}etc/xpra/conf.d/** r,
  /home/virtue/.xpra/** rw,
  
  /home/virtue/.cache/ rw,
  /home/virtue/.cache/gstreamer-1.0/ rw,
  /home/virtue/.cache/gstreamer-1.0/** rw,

  /home/virtue/.dbus/ rw,
  /home/virtue/.dbus/session-bus/ rw,
  /home/virtue/.dbus/session-bus/** rw,

  /home/virtue/.*-fakexinerama rw,
  /home/virtue/.fakexinerama rw,

  /home/virtue/.Xauthority* lrw,
  /{,docker/overlay2/*/diff/}home/virtue/.xpra/pulse/ r,

  /run/xpra/ rw,
  /etc/xpra/xpra.conf r,

  ########################
  # Devices & Interfaces
  ########################
  /sys/devices/virtual/misc/uinput/uevent r,
  /sys/module/apparmor/parameters/enabled r,
  /proc/sys/net/core/somaxconn r,
  /proc/sys/net/unix/max_dgram_qlen r,
  /proc/sys/net/ipv4/* r,


  ########################
  # Things in /proc
  ########################
  @{PROC}/@{pid}/cmdline r,
  @{PROC}/@{pid}/status r,
  @{PROC}/@{pid}/mounts r,
  @{PROC}/@{pid}/pid r,
  @{PROC}/@{pid}/fd/ r,
  @{PROC}/loadavg r,


  ########################
  # Misc.
  ########################
  # Does not seem to be a way to restrict this further
  /tmp/** rw,
  /etc/lsb-release r,
  /etc/magic r,
  /etc/mime.types r,
  /usr/share/file/** r,
  /etc/lsb-release r,

  /usr/share/X11/xkb/keycodes/evdev r,  
  /etc/pulse/client.conf r,

  /usr/share/alsa/alsa.conf r,
  /{,docker/overlay2/*/diff/}usr/share/alsa/alsa.conf.d/ r,
  /{,docker/overlay2/*/diff/}usr/share/alsa/alsa.conf.d/* r,
  /usr/share/alsa/cards/aliases.conf r,
  /usr/share/alsa/pcm/*.conf r,

  /dev/shm/ r,
  /dev/shm/pulse-shm-* rw,


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
  /usr/sbin/lpadmin rmix,

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
  /{,docker/overlay2/*/diff/}tmp/.X11-unix/ rw,

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
# Note: this is based on a profile from GitHub, and it's probably over-permissioned
# for what we're actually using SSHD for...

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
  /{,docker/overlay2/*/diff/}etc/security/** r,
  /etc/ssh/** r,
  /etc/ssl/openssl.cnf r,
  /usr/sbin/sshd mrix,
  /var/log/btmp rw,
  owner /{,var/}run/sshd{,.init}.pid wl,
  owner /{,var/}run/systemd/notify w,
  @{HOME}/.ssh/authorized_keys{,2} r,

  /home/virtue/sshd_config r,
  /home/virtue/.ssh/* r,
  /home/virtue/.cache/ rw,
  /home/virtue/.cache/** rw,
  /home/virtue/.cache/motd.legal-displayed rw,

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

  /etc/legal r,
  /etc/motd r,
  /{,var/}run/motd{,.dynamic}{,.new} rw,
  /tmp/ssh-[a-zA-Z0-9]*/ w,
  /tmp/ssh-[a-zA-Z0-9]*/agent.[0-9]* wl,

  # This is for shells launched by SSHD
  profile ssh_shell flags=(attach_disconnected,mediate_deleted) {
    #include <abstractions/consoles>
    #include <abstractions/bash>
    #include <abstractions/authentication>

    /dev/null rw,

    /{,docker/overlay2/*/diff/}etc/ld.so.cache r,
    /{,docker/overlay2/*/diff/}lib/x86_64-linux-gnu/*.so mr,

    /run/motd.dynamic.new rw,

    /bin/dash rmix,
  }
}

# -------------------------------- crossover ------------------------------------

profile crossover flags=(complain,attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/fonts>
  #include <abstractions/gnome>
  #include <abstractions/nameservice>
  #include <abstractions/perl>
  #include <abstractions/python>

  ###############################
  # Sockets
  ###############################
  unix (send, receive, connect) peer=(addr="@/tmp/.X11-unix/X0"),


  ###############################
  # Python
  ###############################
  /usr/bin/env rmix,
  /usr/bin/python2.7 rmix,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python{2.[4-7],3.[0-5]}/**.{py,pyc,so}           mr,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python{2.[4-7],3.[0-5]}/**.{egg,py,pth}       r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python{2.[4-7],3.[0-5]}/{site,dist}-packages/ r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python{2.[4-7],3.[0-5]}/{site,dist}-packages/** r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python3.[0-5]/            r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python3.[0-5]/*/            r,
  /{,docker/overlay2/*/diff/}usr/lib{,32,64}/python3.[0-5]/lib-dynload/*.so            mr,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python{2.[4-7],3.[0-5]}/**.{pyc,so}           mr,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python{2.[4-7],3.[0-5]}/**.{egg,py,pth}       r,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python{2.[4-7],3.[0-5]}/{site,dist}-packages/ r,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python{2.[4-7],3.[0-5]}/{site,dist}-packages/** r,
  /{,docker/overlay2/*/diff/}usr/local/lib{,32,64}/python3.[0-5]/lib-dynload/*.so            mr,
  /{,docker/overlay2/*/diff/}usr/lib/python3/dist-packages/                  r,
  /{,docker/overlay2/*/diff/}usr/lib/python3/dist-packages/**.so                   mr,


  ###############################
  # Crossover Core
  ###############################
  /opt/cxoffice/bin/crossover r,

  /opt/cxoffice/lib/python/*.py r,
  /opt/cxoffice/lib/python/*.pyc rw,
  /opt/cxoffice/lib/python/**/*.py r,
  /opt/cxoffice/lib/python/**/*.pyc rw,
  /opt/cxoffice/lib/python/glade/*.ui r,

  /opt/cxoffice/lib/perl/*.pm r,

  /{,docker/overlay2/*/diff/}opt/cxoffice/share/** r,

  /{,docker/overlay2/*/diff/}opt/cxoffice/support/ r,
  /{,docker/overlay2/*/diff/}opt/cxoffice/support/** r,

  /opt/cxoffice/etc/cxoffice.conf r,
  /{,docker/overlay2/*/diff/}home/virtue/.cxoffice/ rw,

  /opt/cxoffice/bin/cxassoc rmix,
  /opt/cxoffice/bin/cxbottle rmix,
  /opt/cxoffice/bin/cxdiag rmix,
  /opt/cxoffice/bin/cxmenu rmix,
  /opt/cxoffice/bin/cxstart rmix,
  /opt/cxoffice/bin/cxupdatecheck rmix,
  /opt/cxoffice/bin/wine rmix,
  /opt/cxoffice/bin/wineloader rmpix -> wineloader,


  ###############################
  # /proc
  ###############################
  @{PROC}/@{pid}/cmdline r,
  @{PROC}/@{pid}/status r,
  @{PROC}/@{pid}/mounts r,
  @{PROC}/@{pid}/pid r,
  @{PROC}/@{pid}/fd/ r,


  ###############################
  # Helpers
  ###############################
  /bin/dash rmix,
  /bin/egrep rmix,
  /bin/grep rmix,


  ###############################
  # Misc.
  ###############################
  /home/virtue/.Xauthority r,
  /home/virtue/.xpra/xpra/*.log rw,
  /{,docker/overlay2/*/diff/}tmp/ rw,
  /{,docker/overlay2/*/diff/}tmp/** rw, 
  /dev/shm/* lrw,
  /usr/share/mime/** r,
  /etc/drirc r,
  /etc/fstab r,

  # Font stuff that's broken because of Docker overlay
  /{,docker/overlay2/*/diff/}etc/fonts/conf.d/ r,
  /{,docker/overlay2/*/diff/}etc/fonts/conf.d/** r,
  /{,docker/overlay2/*/diff/}usr/local/share/fonts/ r,
  /{,docker/overlay2/*/diff/}usr/local/share/fonts/** r,

  /var/cache/fontconfig/ rw,
  /home/virtue/.cache/fontconfig/ rw,
  /home/virtue/.cache/fontconfig/** rw,

  /home/virtue/.config/gtk-2.0/ rw,

  /{,docker/overlay2/*/diff/}usr/share/{icons,pixmaps,fonts,poppler}/ r,
  /{,docker/overlay2/*/diff/}usr/share/{icons,pixmaps,fonts,poppler}/** r,

  /{,docker/overlay2/*/diff/}etc/ld.so.cache r,
  /{,docker/overlay2/*/diff/}lib/x86_64-linux-gnu/*.so mr,
  
  /{,docker/overlay2/*/diff/}usr/lib/x86_64-linux-gnu/gio/modules/ r,


  ##################################################################################
  #                                                                                #
  #                 THIS IS THE ACTUAL APPLICATION-RELEVANT PART!                  #
  #                                                                                #  
  ##################################################################################

  /{,docker/overlay2/*/diff/} r,
  /home/virtue/.cxoffice/logs/ rw,
  /tmp/cxlog.cxlog ra,

  /home/virtue/.cxoffice/cxoffice.conf rw,
  /home/virtue/.cxoffice/cxoffice.conf.tmp rw,

  /home/virtue/.cxoffice/PuTTY/*.conf r,
  /home/virtue/.cxoffice/PuTTY/*.reg r,
  /home/virtue/.cxoffice/PuTTY/windata/** r,

}

# -------------------------------- wineloader ------------------------------------

profile wineloader flags=(complain,attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/authentication>
  #include <abstractions/nameservice>
  #include <abstractions/python>

  /{,docker/overlay2/*/diff/}home/virtue/ r,
  /home/virtue/.xpra/xpra/*.log rw,

  /opt/cxoffice/lib/lib*.so* rm,  
  /opt/cxoffice/lib/wine/*.so rm,

  /opt/cxoffice/bin/wine-preloader rmpix -> wine_preloader,
  /opt/cxoffice/bin/* rmix,
  
  /home/virtue/.cxoffice/PuTTY/ rw,
  /home/virtue/.cxoffice/PuTTY/** rw,

  /tmp/cxlog.cxlog ra,

}

profile wine_preloader flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/fonts>
  #include <abstractions/nameservice>

  network unix stream,

  /{,docker/overlay2/*/diff/}home/virtue/ r,
  /tmp/cxlog.cxlog ra,

  "/home/virtue/.cxoffice/PuTTY/drive_c/Program Files/PuTTY/putty.exe" r,
  /home/*/.cxoffice/PuTTY/drive_c/**/ r,
  /home/virtue/ r,
  /home/virtue/.cache/fontconfig/* r,
  /home/virtue/.cxoffice/PuTTY/drive_c/ r,
  /home/virtue/.cxoffice/PuTTY/drive_c/*/ r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/advapi32.dll r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/crypt32.dll r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/gdi32.dll r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/imm32.dll r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/rsaenh.dll r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/user32.dll r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/version.dll r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/wineboot.exe r,
  /home/virtue/.cxoffice/PuTTY/drive_c/windows/system32/winewrapper.exe r,
  /lib/i386-linux-gnu/ld-*.so mr,
  /opt/cxoffice/bin/wine-preloader r,
  /opt/cxoffice/bin/wineloader mr,
  /opt/cxoffice/etc/license.sig r,
  /opt/cxoffice/etc/license.txt r,
  /opt/cxoffice/lib/lib*so* mr,
  /opt/cxoffice/lib/wine/* mr,
  /opt/cxoffice/share/crossover/data/tie.pub r,
  /proc/*/mounts r,
  /proc/scsi/scsi r,

}