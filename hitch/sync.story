Sync:
  about: |
    Build ubuntu, install 
  given:
    vmname: mytrusty
    boxname: ubuntu-trusty-64
    setup: |
      import hitchbuildvagrant

      ubuntu = hitchbuildvagrant.Box(vmname, boxname)\
                                .with_download_path("/path/to/share")\
                                .which_syncs(local_sync_path, "/remotesync")

      class PythonSnapshot(hitchbuildvagrant.Snapshot):
          def setup(self):
              pass

      snapshot = PythonSnapshot("mysynced", ubuntu).with_build_path(".")

  steps:
  - Write to localsync:
      filepath1.txt: cabbage

  - Run: |
      snapshot.ensure_built()
      assert "cabbage" in snapshot.cmd("cat /remotesync/filepath1.txt").output(), \
          "Expected 'cabbage' got {}".format(snapshot.cmd("cat /remotesync/filepath1.txt").output())
      snapshot.shutdown()

  - Delete localsync file: filepath1.txt

  - Write to localsync:
      filepath2.txt: sprouts

  - Run: |
      snapshot.ensure_built()
      assert "sprouts" in snapshot.cmd("cat /remotesync/filepath2.txt").output(), \
          "Expected 'sprouts' got {}".format(snapshot.cmd("cat /remotesync/filepath2.txt").output())

      assert "No such file" in snapshot.cmd("cat /remotesync/filepath1.txt").ignore_errors().output(), \
          "Expected 'No such file' got {}".format(
              snapshot.cmd("cat /remotesync/filepath1.txt").ignore_errors().output()
          )
      snapshot.shutdown()
