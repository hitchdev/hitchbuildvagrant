Ubuntu Vagrant box:
  about: |
    Build ubuntu
  given:
    boxname: ubuntu-trusty-64
    issue: Ubuntu 14.04
    setup: |
      import hitchbuildvagrant

      ubuntu = hitchbuildvagrant.Box("myvm", boxname)\
                                .with_build_path(".")\
                                .with_download_path("/path/to/share")
  steps:
  - Run: |
      ubuntu.ensure_built()
      assert issue in ubuntu.cmd("cat /etc/issue").output()
      ubuntu.destroy()

