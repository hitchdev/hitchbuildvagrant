from slugify import slugify
import hitchbuild


class Snapshot(hitchbuild.HitchBuild):
    def __init__(self, name, box):
        self._name = name
        self.box = self.as_dependency(box)
        self._slug = slugify(name)

    def fingerprint(self):
        return (self._slug, self.box._slug)

    @property
    def vagrant_snapshot(self):
        return self.box.vagrant("snapshot")

    def setup(self):
        pass

    @property
    def cmd(self):
        return self.box.cmd

    def shutdown(self):
        self.box.shutdown()

    def build(self):
        if self._slug in self.vagrant_snapshot("list").output().strip().split('\n'):
            self.vagrant_snapshot("restore", self._slug, "--no-provision").run()
            self.box.vagrant("rsync").run()
        else:
            self.box.ensure_built()
            self.box.ensure_running()
            self.setup()
            self.vagrant_snapshot("save", self._slug).run()
