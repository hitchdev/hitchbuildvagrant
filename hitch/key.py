from hitchstory import StoryCollection, BaseEngine
from hitchstory import GivenDefinition, GivenProperty, InfoDefinition, InfoProperty
from hitchstory import validate, HitchStoryException, no_stacktrace_for
from hitchrun import expected
from strictyaml import Str, MapPattern, Optional, Float, Enum
from pathquery import pathquery
from commandlib import Command, python_bin
from commandlib import python
from hitchrun import hitch_maintenance
from hitchrun import DIR
from hitchrunpy import ExamplePythonCode, ExpectedExceptionMessageWasDifferent, HitchRunPyException
from templex import Templex
import hitchpylibrarytoolkit
import hitchbuildpy


class Engine(BaseEngine):
    """Python engine for running tests."""

    given_definition = GivenDefinition(
        setup=GivenProperty(Str()),
        boxname=GivenProperty(Str()),
        vmname=GivenProperty(Str()),
        issue=GivenProperty(Str()),
        files=GivenProperty(MapPattern(Str(), Str())),
        python_version=GivenProperty(Str()),
    )

    info_definition = InfoDefinition(
        status=InfoProperty(schema=Enum(["experimental", "stable"])),
        docs=InfoProperty(schema=Str()),
    )

    def __init__(self, paths, settings):
        self.path = paths
        self.settings = settings

    def set_up(self):
        """Set up your applications and the test environment."""
        self.path.cachestate = self.path.gen.joinpath("cachestate")
        self.path.state = self.path.gen.joinpath("state")
        self.path.working_dir = self.path.gen.joinpath("working")
        self.path.build_path = self.path.gen.joinpath("build_path")

        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        if self.path.build_path.exists():
            self.path.build_path.rmtree(ignore_errors=True)
        self.path.build_path.mkdir()

        self.python = hitchpylibrarytoolkit.project_build(
            "hitchbuildvagrant", self.path, self.given.get("python_version", "3.7.0")
        ).bin.python


        if not self.path.cachestate.exists():
            self.path.cachestate.mkdir()

        for filename, contents in self.given.get("files", {}).items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(contents)

        if self.path.working_dir.exists():
            self.path.working_dir.rmtree(ignore_errors=True)
        self.path.working_dir.mkdir()

        self.example_py_code = (
            ExamplePythonCode(self.python, self.path.state)
            .with_setup_code(
                self.given.get("setup", "")
                .replace("/path/to/share", self.path.cachestate)
            )
            .with_terminal_size(160, 100)
            .with_long_strings(
                share=str(self.path.cachestate),
                build_path=str(self.path.build_path),
                issue=str(self.given['issue']),
                boxname=str(self.given['boxname']),
                vmname=str(self.given['vmname']),
            )
        )

    @no_stacktrace_for(HitchRunPyException)
    def run(self, code):
        self.example_py_code.with_code(code).run()

    @no_stacktrace_for(AssertionError)
    def output_ends_with(self, contents):
        Templex(contents).assert_match(self.result.output.split("\n")[-1])

    def write_file(self, filename, contents):
        self.path.state.joinpath(filename).write_text(contents)

    def raises_exception(self, message=None, exception_type=None):
        try:
            result = self.example_python_code.expect_exceptions().run(
                self.path.state, self.python
            )
            result.exception_was_raised(exception_type, message.strip())
        except ExpectedExceptionMessageWasDifferent as error:
            if self.settings.get("rewrite"):
                self.current_step.update(message=error.actual_message)
            else:
                raise

    def file_contains(self, filename, contents):
        assert (
            self.path.working_dir.joinpath(filename).bytes().decode("utf8") == contents
        )

    @validate(duration=Float())
    def sleep(self, duration):
        import time

        time.sleep(duration)

    def pause(self, message="Pause"):
        import IPython

        IPython.embed()

    def tear_down(self):
        for vagrantfile in pathquery(self.path.state).named("Vagrantfile"):
            Command("vagrant", "destroy", "-f").in_dir(vagrantfile.abspath().dirname()).run()


@expected(HitchStoryException)
def bdd(*words):
    """
    Run story with words.
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"), Engine(DIR, {"rewrite": True})
    ).shortcut(*words).play()

def regression():
    """
    Regression test - run all tests and linter.
    """
    lint()
    StoryCollection(
        pathquery(DIR.key).ext("story"), Engine(DIR, {"overwrite artefacts": False})
    ).only_uninherited().ordered_by_name().play()


def cleancache():
    """
    Clean the cache state.
    """
    DIR.gen.joinpath("cachestate").rmtree(ignore_errors=True)
    print("Done")


def reformat():
    """
    Reformat using black and then relint.
    """
    hitchpylibrarytoolkit.reformat(DIR.project, "hitchbuildvagrant")


def lint():
    """
    Lint project code and hitch code.
    """
    hitchpylibrarytoolkit.lint(DIR.project, "hitchbuildvagrant")



def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    hitchpylibrarytoolkit.deploy(DIR.project, "hitchbuildvagrant", version)

