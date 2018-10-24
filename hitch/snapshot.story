Snapshot:
  about: |
    Build ubuntu, install 
  given:
    vmname: mytrusty
    boxname: ubuntu-trusty-64
    setup: |
      import hitchbuildvagrant

      ubuntu = hitchbuildvagrant.Box(vmname, boxname)\
                                .with_download_path("/path/to/share")
      
      
      class PythonSnapshot(hitchbuildvagrant.Snapshot):
          def setup(self):
              self.cmd("sudo apt-get install python3 -y").run()
      
      snapshot = PythonSnapshot("mypythonsnapshot", ubuntu).with_build_path(".")

  steps:
  - Run: |
      snapshot.ensure_built()
      assert "Python" in snapshot.cmd("python3 --version").output(), \
          "Expected 'Python' got {}".format(issue, snapshot.cmd("python3 --version").output())
      snapshot.shutdown()

  - Run: |
      snapshot.ensure_built()
      assert "Python" in snapshot.cmd("python3 --version").output(), \
          "Expected 'Python' got {}".format(issue, snapshot.cmd("python3 --version").output())
      snapshot.shutdown()
