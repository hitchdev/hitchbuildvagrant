Ubuntu Vagrant box:
  about: |
    Build ubuntu
  given:
    setup: |
      import hitchbuildvagrant

      ubuntu = hitchbuildvagrant.Box("myvm", "ubuntu-trusty-64")\
                                .with_build_path(".")\
                                .with_download_path("/path/to/share")
  steps:
  - Run: |
      ubuntu.ensure_built()
      assert "Ubuntu 14.04" in ubuntu.cmd("cat /etc/issue").output()
      ubuntu.destroy()

