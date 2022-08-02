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
#  exports_sources = "patches/*.patch"
#  tool_requires = "libtool/[>=2.4.6]"

  def source(self):
    version_underline = self.version.replace(".", "_")
    url = f"https://github.com/DOCGroup/ACE_TAO/releases/download/ACE%2BTAO-{version_underline}/ACE+TAO-src-{self.version}.tar.bz2"
    tools.get(url, md5="046f004b54e4117a49c63b2f4f99a214", verify=False)

#  def build(self):
#    self.run("./autogen.sh && ./configure", cwd="log4cpp");
#    cmake = self._configure_cmake()
#    cmake.build()
#
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

