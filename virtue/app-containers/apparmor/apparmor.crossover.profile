

#include <tunables/global>


profile docker-crossover flags=(attach_disconnected,mediate_deleted) {

  #include <abstractions/base>


  network,
  capability,
  file,
  umount,

  ptrace trace peer=*,

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

  # /dev/tty* rw,
  # /usr/bin/gedit rix,

  # Allowing to change these doesn't seem to be a good idea
  # And denying it should be harmless
  deny /{,var/}run/user/*/dconf/user w,
  deny @{HOME}/.config/dconf/user w,
  deny /var/cache/fontconfig/ w,
  deny @{HOME}/.cache/fontconfig/** w,

}
