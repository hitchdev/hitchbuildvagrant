from hitchbuildvagrant import utils
from commandlib import Command
from slugify import slugify
from path import Path
from copy import copy
import hitchbuild
import jinja2
import json


TEMPLATE_DIR = Path(__file__).realpath().dirname() / "templates"


STANDARD_BOXES = json.loads(TEMPLATE_DIR.joinpath("boxdata.json").text())


class Box(hitchbuild.HitchBuild):
    def __init__(self, name, machine):
        self._name = name
        self.machine = machine
        self._download_path = None
        self._slug = slugify(name, separator="_")
        self._sync_from_location = None
        self._sync_to_location = None

    def _retrieve(self):
        if not self.download_to.exists():
            utils.download_file(self.download_to, STANDARD_BOXES[self.machine]["url"])

    def with_download_path(self, download_path):
        new_box = copy(self)
        new_box._download_path = Path(download_path)
        return new_box

    def which_syncs(self, path_from, path_to):
        new_box = copy(self)
        new_box._sync_from_location = Path(path_from).abspath()
        new_box._sync_to_location = path_to
        assert new_box._sync_from_location.exists(), \
            "Sync from location {} should exist.".format(new_box._sync_from_location)
        return new_box

    def fingerprint(self):
        return (self._slug, self.machine)

    @property
    def download_to(self):
        directory = (
            self.basepath if self._download_path is None else self._download_path
        )
        return directory.joinpath("{}.iso".format(self.machine)).abspath()

    @property
    def vagrant_file(self):
        return jinja2.Template(TEMPLATE_DIR.joinpath("linux.jinja2").text()).render(
            machine_name=self._slug,
            location=self.download_to,
            sync_from_location=self._sync_from_location,
            sync_to_location=self._sync_to_location,
        )

    @property
    def vagrant(self):
        return Command("vagrant").in_dir(self.basepath)

    def build(self):
        self._retrieve()
        if not self.basepath.exists():
            self.basepath.mkdir()
            self.basepath.joinpath("Vagrantfile").write_text(self.vagrant_file)
            self.vagrant("up").run()
            self.vagrant("snapshot", "save", self._slug).run()
            self.vagrant("halt").run()

    def ensure_running(self):
        self.vagrant("snapshot", "restore", self._slug, "--no-provision").run()

    @property
    def cmd(self):
        return self.vagrant("ssh", "-c")

    def shutdown(self):
        self.vagrant("halt").run()

    def destroy(self):
        self.vagrant("destroy", "-f").run()

    @property
    def basepath(self):
        return self.build_path.joinpath(self._slug)
