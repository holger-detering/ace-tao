import os

from conans import ConanFile, CMake, tools

# TODO: generator? cmake...
class Log4cppTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"
    requires = "ace+tao/6.5.17@"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(".%spackage_test" % os.sep)
