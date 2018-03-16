

#include <tunables/global>


profile docker-firefox flags=(attach_disconnected,mediate_deleted) {

  #include <abstractions/base>


  network,
  capability,
  file,
  umount,

  deny @{PROC}/* w,   # deny write for all files directly in /proc (not in a subdir)
  # deny write to files not in /proc/<number>/** or /proc/sys/**
  deny @{PROC}/{[^1-9],[^1-9][^0-9],[^1-9s][^0-9y][^0-9s],[^1-9][^0-9][^0-9][^0-9]*}/** w,
  deny @{PROC}/sys/[^k]** w,  # deny /proc/sys except /proc/sys/k* (effectively /proc/sys/kernel)
  deny @{PROC}/sys/kernel/{?,??,[^s][^h][^m]**} w,  # deny everything except shm* in /proc/sys/kernel/
  deny @{PROC}/sysrq-trigger rwklx,
  deny @{PROC}/mem rwklx,
  deny @{PROC}/kmem rwklx,
  deny @{PROC}/kcore rwklx,

  deny mount,

  deny /sys/[^f]*/** wklx,
  deny /sys/f[^s]*/** wklx,
  deny /sys/fs/[^c]*/** wklx,
  deny /sys/fs/c[^g]*/** wklx,
  deny /sys/fs/cg[^r]*/** wklx,
  deny /sys/firmware/efi/efivars/** rwklx,
  deny /sys/kernel/security/** rwklx,


  # suppress ptrace denials when using 'docker ps' or using 'ps' inside a container
  # ptrace (trace,read) peer=docker-default,

   # Launcher
   /dev/tty* rw,
   /usr/{lib/firefox,bin}/firefox rix,
   /usr/lib/xulrunner/xulrunner-stub ix,

   owner @{HOME}/.mozilla/firefox/** rwk,
   owner @{HOME}/.cache/ rw,
   owner @{HOME}/.cache/mozilla/ rw,
   owner @{HOME}/.cache/mozilla/firefox/ rw,
   owner @{HOME}/.cache/mozilla/firefox/** rwk,
   owner @{HOME}/.cache/gstreamer-*/ rw,
   owner @{HOME}/.cache/gstreamer-*/** rw,

   /opt/netscape/plugins/ r,
   /opt/netscape/plugins/** mr,
   owner @{HOME}/.mozilla/plugins/ r,
   owner @{HOME}/.mozilla/plugins/** mr,
   owner @{HOME}/.mozilla/firefox/*/extensions/** m,
   owner @{HOME}/.mozilla/extensions/** mr,

   # Didn't check what this one is for
   deny @{HOME}/.mozilla/systemextensionsdev/ rw,
   deny @{HOME}/.mozilla/systemextensionsdev/** rw,

   /etc/mime.types r,
   /etc/mailcap r,
   /usr/share/ r,
   /usr/share/mime/ r,
   /usr/share/glib-*/schemas/* r,
   /usr/share/applications/screensavers/ r,
   owner @{HOME}/.local/share/ r,
   owner @{HOME}/.local/share/applications/ r,
   owner @{HOME}/.local/share/applications/** r,

   owner @{PROC}/@{pid}/fd/ r,
   owner @{PROC}/@{pid}/mountinfo r,
   owner @{PROC}/@{pid}/statm r, # for about:memory
   owner @{PROC}/@{pid}/task/[0-9]*/stat r,
   @{PROC}/@{pid}/net/arp r, # for local "network id", to detect changes

   # Wants more and more info on pci devs with each version
   # Didn't check what for, probably some hw-change detection
   deny /dev/ r,
   deny /sys/devices/pci**/{config,vendor,device} r,

   # Used in private mode
   /usr/bin/shred ix,

   # Allowing to change these doesn't seem to be a good idea
   # And denying it should be harmless
   deny /{,var/}run/user/*/dconf/user w,
   deny @{HOME}/.config/dconf/user w,
   deny /var/cache/fontconfig/ w,
   deny @{HOME}/.cache/fontconfig/** w,

   ## Site-local paths
   # Images in file selection dialogs
   owner @{HOME}/.thumbnails/** w,
   # downloads
   /etc/fstab r,

   ## New e10s profiles
   /usr/lib/firefox/plugin-container ix, # used to create new tab
   audit deny /dev/shm/org.chromium.Chromium.* rw, # used by Chromium
   owner /dev/shm/org.chromium.* rwmk,
}
