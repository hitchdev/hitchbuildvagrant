Ubuntu Vagrant box:
  about: |
    Build ubuntu
  given:
    vmname: mytrusty
    boxname: ubuntu-trusty-64
    issue: Ubuntu 14.04
    setup: |
      import hitchbuildvagrant

      ubuntu = hitchbuildvagrant.Box(vmname, boxname)\
                                .with_build_path(".")\
                                .with_download_path("/path/to/share")
  steps:
  - Run: |
      ubuntu.ensure_built()
      assert issue in ubuntu.cmd("cat /etc/issue").output(), \
          "Expected {} got {}".format(issue, ubuntu.cmd("cat /etc/issue").output())
      ubuntu.destroy()

  variations:
    trusty 14.04:
      given:
        vmname: mytrusty
        boxname: ubuntu-trusty-64
        issue: Ubuntu 14.04

    bionic 18.04:
      given:
        vmname: mybionic
        boxname: ubuntu-bionic-64
        issue: Ubuntu 18.04
