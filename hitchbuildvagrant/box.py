from commandlib import CommandPath, Command
from hitchbuildvagrant import utils
from slugify import slugify
from path import Path
from copy import copy
import hitchbuild
import jinja2


TEMPLATE_DIR = Path(__file__).realpath().dirname() / "templates"


STANDARD_BOXES = {
    "ubuntu-trusty-64": {
        "url": "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box",
        "template": "linux.jinja2",
    },
    # ubuntu-bionic0-64
}


class Box(hitchbuild.HitchBuild):
    def __init__(self, name, machine):
        self._name = name
        self.machine = machine
        self._download_path = None
        self._slug = slugify(name, separator="_")

    def _retrieve(self):
        if not self.download_to.exists():
            utils.download_file(self.download_to, STANDARD_BOXES[self.machine]['url'])

    def with_download_path(self, download_path):
        new_box = copy(self)
        new_box._download_path = Path(download_path)
        return new_box

    def fingerprint(self):
        return (self._slug, self.machine)

    @property
    def download_to(self):
        directory = self.basepath if self._download_path is None else self._download_path
        return directory.joinpath("{}.iso".format(self.machine)).abspath()

    @property
    def vagrant_file(self):
        return jinja2.Template(TEMPLATE_DIR.joinpath("linux.jinja2").text()).render(
            machine_name=self._slug,
            location=self.download_to,
        )

    @property
    def vagrant(self):
        return Command("vagrant").in_dir(self.basepath)

    def build(self):
        self._retrieve()
        if self.basepath.exists():
            self.basepath.rmtree()
        self.basepath.mkdir()
        self.basepath.joinpath("Vagrantfile").write_text(self.vagrant_file)
        self.vagrant("up").run()

    @property
    def cmd(self):
        return self.vagrant("ssh", "-c")

    def destroy(self):
        self.vagrant("destroy", "-f").run()

    @property
    def basepath(self):
        return self.build_path.joinpath(self._slug)

