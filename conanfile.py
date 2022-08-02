from conans import ConanFile, AutoToolsBuildEnvironment, tools

class Log4cppConan(ConanFile):
  name = "ace+tao"
  version = "6.5.17"
  license = "DOC"
  author = "Douglas C. Schmidt <d.schmidt@vanderbilt.edu>"
  url = "https://www.dre.vanderbilt.edu/TAO"
  description = """\
The ADAPTIVE Communication Environment (ACE) is an object-oriented
(OO) toolkit that implements fundamental design patterns for
communication software.

TAO (The ACE ORB) is a freely available, open-source implementation
of a CORBA 3.x-compliant ORB that supports real-time extensions.
"""
  topics = ("c++", "CORBA")
  settings = "os", "compiler", "build_type", "arch"
  options = {"shared": [True, False]}
  default_options = {"shared": True}
  generators = "cmake"

  def source(self):
    # url = f"https://github.com/DOCGroup/ACE_TAO/releases/download/ACE%2BTAO-{self.version.replace('.', '_')}/ACE+TAO-src-{self.version}.tar.bz2"
    url = f"http://localhost:5555/DOCGroup/ACE_TAO/releases/download/ACE%2BTAO-{self.version.replace('.', '_')}/ACE+TAO-src-{self.version}.tar.bz2"
    tools.get(url, md5="046f004b54e4117a49c63b2f4f99a214", verify=False)
    tools.save("ACE_wrappers/ace/config.h", """\
#include "ace/config-linux.h"
""")
    tools.save("ACE_wrappers/include/makeinclude/platform_macros.GNU", """\
include $(ACE_ROOT)/include/makeinclude/platform_linux.GNU
""")

  def build(self):
    ace_root = f"{self.source_folder}/ACE_wrappers"
    tao_root = f"{ace_root}/TAO"
    with tools.environment_append({"ACE_ROOT": ace_root, "TAO_ROOT": tao_root}):
      with tools.chdir(tao_root):
        self.run("$ACE_ROOT/bin/mwc.pl TAO_ACE.mwc -type gnuace")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.make()

#  def package(self):
#    cmake = self._configure_cmake()
#    cmake.install()
#
#  def package_info(self):
#    if self.settings.build_type == "Debug":
#      self.cpp_info.libs = ["log4cppD"]
#    else:
#      self.cpp_info.libs = ["log4cpp"]
#    if self.settings.os == "Linux":
#      self.cpp_info.libs.append("pthread")

