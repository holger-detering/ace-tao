from conan import ConanFile
from conan.tools.files import chdir, check_md5, get, save, unzip
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conan.tools.env import Environment

import os

class Log4cppConan(ConanFile):
  name = "ace+tao"
  version = "7.0.9"
  license = "DOC"
  author = "Holger Detering <freelance@detering-springhoe.de>"
  url = "https://github.com/holger-detering/ace+tao"
  homepage = "https://www.dre.vanderbilt.edu/TAO"
  description = """\
The ADAPTIVE Communication Environment (ACE) is an object-oriented
(OO) toolkit that implements fundamental design patterns for
communication software.

TAO (The ACE ORB) is a freely available, open-source implementation
of a CORBA 3.x-compliant ORB that supports real-time extensions.
"""
  topics = ("c++", "CORBA")
  settings = "os", "compiler", "build_type", "arch"
  options = {
      "with_bzip2": [True, False],
      "with_xerces": [True, False],
      "with_zlib": [True, False]
      }
  default_options = {
      "with_bzip2": False,
      "with_xerces": False,
      "with_zlib": False
      }
  exports_sources = f"sources/ACE+TAO-src-{version}.tar.bz2"
  package_type = "shared-library"

  def _fetch_sources(self):
    tarball_name = f"ACE+TAO-src-{self.version}.tar.bz2"
    url = f"https://github.com/DOCGroup/ACE_TAO/releases/download/ACE%2BTAO-{self.version.replace('.', '_')}/" + tarball_name
    # url = f"http://localhost:5555/DOCGroup/ACE_TAO/releases/download/ACE%2BTAO-{self.version.replace('.', '_')}/" + tarball_name
    source_path = os.path.join("sources", tarball_name)
    checksums = self.conan_data["checksums"][self.version][0]
    if os.path.isfile(source_path):
      check_md5(self, source_path, checksums["md5"])
      unzip(self, source_path)
    else:
      get(self, url, md5=checksums["md5"], verify=False)

  def source(self):
    self._fetch_sources()
    save(self, "ACE_wrappers/ace/config.h", """\
#include "ace/config-linux.h"
""")
    save(self, "ACE_wrappers/include/makeinclude/platform_macros.GNU", """\
include $(ACE_ROOT)/include/makeinclude/platform_linux.GNU
""")

  def requirements(self):
    if self.options.with_bzip2:
      self.requires("bzip2/1.0.8")
    if self.options.with_xerces:
      self.requires("xerces-c/3.2.2")
    if self.options.with_zlib:
      self.requires("zlib/1.2.11")

  def generate(self):
    self.ace_root = os.path.join(self.source_folder, "ACE_wrappers")
    self.tao_root = os.path.join(self.ace_root, "TAO")
    ad = AutotoolsDeps(self)
    ad.environment.define("ACE_ROOT", self.ace_root)
    ad.environment.define("TAO_ROOT", self.tao_root)
    ad.environment.define("INSTALL_PREFIX", "/")
    ad.generate()
    tc = AutotoolsToolchain(self)
    if self.options.with_bzip2:
      tc.make_args.append("bzip2=1")
    if self.options.with_xerces:
      tc.make_args.append("xerces=1")
    if self.options.with_zlib:
      tc.make_args.append("zlib=1")
    if self.settings.build_type == "Debug" or self.settings.build_type == "RelWithDebInfo":
      tc.make_args.append("debug=1")
    if self.settings.build_type == "Debug":
      tc.make_args.append("optimize=0")
    tc.generate()

  def build(self):
    features = ""
    if self.options.with_bzip2:
      features += "bzip2=1\n"
    if self.options.with_xerces:
      features += "xerces=1\n"
    if self.options.with_zlib:
      features += "zlib=1\n"
    save(self, os.path.join(self.ace_root, "MPC/config/default.features"), features)
    with chdir(self, self.tao_root):
      self.run("$ACE_ROOT/bin/mwc.pl TAO_ACE.mwc -type gnuace")
      autotools = Autotools(self)
      autotools.make()

  def package(self):
    with chdir(self, self.tao_root):
      autotools = Autotools(self)
      autotools.install()

  def package_info(self):
    self.cpp_info.set_property("cmake_target_name", "ace+tao")
    self.cpp_info.set_property("cmake_find_mode", "both")
    self.cpp_info.components["ACE_ETCL_Parser"].set_property("cmake_target_name", "ace+tao::ACE_ETCL_Parser")
    self.cpp_info.components["ACE_ETCL_Parser"].libs = ["ACE_ETCL_Parser"]
    self.cpp_info.components["ACE_ETCL_Parser"].requires = ["ACE_ETCL"]
    self.cpp_info.components["ACE_ETCL"].set_property("cmake_target_name", "ace+tao::ACE_ETCL")
    self.cpp_info.components["ACE_ETCL"].libs = ["ACE_ETCL"]
    self.cpp_info.components["ACE_ETCL"].requires = ["ACE"]
    self.cpp_info.components["ACE_HTBP"].set_property("cmake_target_name", "ace+tao::ACE_HTBP")
    self.cpp_info.components["ACE_HTBP"].libs = ["ACE_HTBP"]
    self.cpp_info.components["ACE_HTBP"].requires = ["ACE"]
    self.cpp_info.components["ACE_INet"].set_property("cmake_target_name", "ace+tao::ACE_INet")
    self.cpp_info.components["ACE_INet"].libs = ["ACE_INet"]
    self.cpp_info.components["ACE_INet"].requires = ["ACE"]
    self.cpp_info.components["ACE_Monitor_Control"].set_property("cmake_target_name", "ace+tao::ACE_Monitor_Control")
    self.cpp_info.components["ACE_Monitor_Control"].libs = ["ACE_Monitor_Control"]
    self.cpp_info.components["ACE_Monitor_Control"].requires = ["ACE_ETCL_Parser"]
    self.cpp_info.components["ACE"].set_property("cmake_target_name", "ace+tao::ACE")
    self.cpp_info.components["ACE"].libs = ["ACE"]
    self.cpp_info.components["ACE"].system_libs = ["dl", "rt"]
    if self.options.with_bzip2:
      self.cpp_info.components["ACE"].system_libs.append("bz2")
      self.cpp_info.components["ACE"].requires.append("bzip2::bzip2")
    if self.options.with_xerces:
      self.cpp_info.components["ACE"].system_libs.append("pthread")
      self.cpp_info.components["ACE"].requires.append("xerces-c::xerces-c")
    if self.options.with_zlib:
      self.cpp_info.components["ACE"].system_libs.append("z")
      self.cpp_info.components["ACE"].requires.append("zlib::zlib")
    self.cpp_info.components["ACE_RMCast"].set_property("cmake_target_name", "ace+tao::ACE_RMCast")
    self.cpp_info.components["ACE_RMCast"].libs = ["ACE_RMCast"]
    self.cpp_info.components["ACE_RMCast"].requires = ["ACE"]
    self.cpp_info.components["ACE_TMCast"].set_property("cmake_target_name", "ace+tao::ACE_TMCast")
    self.cpp_info.components["ACE_TMCast"].libs = ["ACE_TMCast"]
    self.cpp_info.components["ACE_TMCast"].requires = ["ACE"]
    self.cpp_info.components["ACEXML_Parser"].set_property("cmake_target_name", "ace+tao::ACEXML_Parser")
    self.cpp_info.components["ACEXML_Parser"].libs = ["ACEXML_Parser"]
    self.cpp_info.components["ACEXML_Parser"].requires = ["ACEXML"]
    self.cpp_info.components["ACEXML"].set_property("cmake_target_name", "ace+tao::ACEXML")
    self.cpp_info.components["ACEXML"].libs = ["ACEXML"]
    self.cpp_info.components["ACEXML"].requires = ["ACE"]
    if self.options.with_xerces:
      self.cpp_info.components["ACE_XML_Utils"].set_property("cmake_target_name", "ace+tao::ACE_XML_Utils")
      self.cpp_info.components["ACE_XML_Utils"].libs = ["ACE_XML_Utils"]
      self.cpp_info.components["ACE_XML_Utils"].requires = ["ACE", "xerces-c::xerces-c"]
    self.cpp_info.components["ACEXML_XML_Svc_Conf_Parser"].set_property("cmake_target_name", "ace+tao::ACEXML_XML_Svc_Conf_Parser")
    self.cpp_info.components["ACEXML_XML_Svc_Conf_Parser"].libs = ["ACEXML_XML_Svc_Conf_Parser"]
    self.cpp_info.components["ACEXML_XML_Svc_Conf_Parser"].requires = ["ACEXML_Parser"]
    self.cpp_info.components["Kokyu"].set_property("cmake_target_name", "ace+tao::Kokyu")
    self.cpp_info.components["Kokyu"].libs = ["Kokyu"]
    self.cpp_info.components["Kokyu"].requires = ["ACE"]
    self.cpp_info.components["TAO_AnyTypeCode"].set_property("cmake_target_name", "ace+tao::TAO_AnyTypeCode")
    self.cpp_info.components["TAO_AnyTypeCode"].libs = ["TAO_AnyTypeCode"]
    self.cpp_info.components["TAO_AnyTypeCode"].requires = ["TAO"]
    self.cpp_info.components["TAO_Async_IORTable"].set_property("cmake_target_name", "ace+tao::TAO_Async_IORTable")
    self.cpp_info.components["TAO_Async_IORTable"].libs = ["TAO_Async_IORTable"]
    self.cpp_info.components["TAO_Async_IORTable"].requires = ["TAO", "TAO_IORTable"]
    self.cpp_info.components["TAO_BiDirGIOP"].set_property("cmake_target_name", "ace+tao::TAO_BiDirGIOP")
    self.cpp_info.components["TAO_BiDirGIOP"].libs = ["TAO_BiDirGIOP"]
    self.cpp_info.components["TAO_BiDirGIOP"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    if self.options.with_bzip2:
      self.cpp_info.components["TAO_Bzip2Compressor"].set_property("cmake_target_name", "ace+tao::TAO_Bzip2Compressor")
      self.cpp_info.components["TAO_Bzip2Compressor"].libs = ["TAO_Bzip2Compressor"]
      self.cpp_info.components["TAO_Bzip2Compressor"].requires = ["TAO_Compression", "bzip2::bzip2"]
    self.cpp_info.components["TAO_CodecFactory"].set_property("cmake_target_name", "ace+tao::TAO_CodecFactory")
    self.cpp_info.components["TAO_CodecFactory"].libs = ["TAO_CodecFactory"]
    self.cpp_info.components["TAO_CodecFactory"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Codeset"].set_property("cmake_target_name", "ace+tao::TAO_Codeset")
    self.cpp_info.components["TAO_Codeset"].libs = ["TAO_Codeset"]
    self.cpp_info.components["TAO_Codeset"].requires = ["TAO"]
    self.cpp_info.components["TAO_Compression"].set_property("cmake_target_name", "ace+tao::TAO_Compression")
    self.cpp_info.components["TAO_Compression"].libs = ["TAO_Compression"]
    self.cpp_info.components["TAO_Compression"].requires = ["TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosConcurrency"].set_property("cmake_target_name", "ace+tao::TAO_CosConcurrency")
    self.cpp_info.components["TAO_CosConcurrency"].libs = ["TAO_CosConcurrency"]
    self.cpp_info.components["TAO_CosConcurrency"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosConcurrency_Serv"].set_property("cmake_target_name", "ace+tao::TAO_CosConcurrency_Serv")
    self.cpp_info.components["TAO_CosConcurrency_Serv"].libs = ["TAO_CosConcurrency_Serv"]
    self.cpp_info.components["TAO_CosConcurrency_Serv"].requires = ["TAO_CosConcurrency_Skel"]
    self.cpp_info.components["TAO_CosConcurrency_Skel"].set_property("cmake_target_name", "ace+tao::TAO_CosConcurrency_Skel")
    self.cpp_info.components["TAO_CosConcurrency_Skel"].libs = ["TAO_CosConcurrency_Skel"]
    self.cpp_info.components["TAO_CosConcurrency_Skel"].requires = ["TAO_CosConcurrency", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosEvent"].set_property("cmake_target_name", "ace+tao::TAO_CosEvent")
    self.cpp_info.components["TAO_CosEvent"].libs = ["TAO_CosEvent"]
    self.cpp_info.components["TAO_CosEvent"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosEvent_Serv"].set_property("cmake_target_name", "ace+tao::TAO_CosEvent_Serv")
    self.cpp_info.components["TAO_CosEvent_Serv"].libs = ["TAO_CosEvent_Serv"]
    self.cpp_info.components["TAO_CosEvent_Serv"].requires = ["TAO_CosEvent_Skel", "TAO_DynamicInterface", "TAO_IFR_Client", "TAO_Messaging", "TAO_CosNaming", "TAO_Svc_Utils"]
    self.cpp_info.components["TAO_CosEvent_Skel"].set_property("cmake_target_name", "ace+tao::TAO_CosEvent_Skel")
    self.cpp_info.components["TAO_CosEvent_Skel"].libs = ["TAO_CosEvent_Skel"]
    self.cpp_info.components["TAO_CosEvent_Skel"].requires = ["TAO_CosEvent", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosLifeCycle"].set_property("cmake_target_name", "ace+tao::TAO_CosLifeCycle")
    self.cpp_info.components["TAO_CosLifeCycle"].libs = ["TAO_CosLifeCycle"]
    self.cpp_info.components["TAO_CosLifeCycle"].requires = ["TAO_CosNaming", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosLifeCycle_Skel"].set_property("cmake_target_name", "ace+tao::TAO_CosLifeCycle_Skel")
    self.cpp_info.components["TAO_CosLifeCycle_Skel"].libs = ["TAO_CosLifeCycle_Skel"]
    self.cpp_info.components["TAO_CosLifeCycle_Skel"].requires = ["TAO_CosLifeCycle", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosLoadBalancing"].set_property("cmake_target_name", "ace+tao::TAO_CosLoadBalancing")
    self.cpp_info.components["TAO_CosLoadBalancing"].libs = ["TAO_CosLoadBalancing"]
    self.cpp_info.components["TAO_CosLoadBalancing"].requires = ["TAO_CosNaming", "TAO_IORManip", "TAO_PortableGroup", "TAO"]
    self.cpp_info.components["TAO_CosNaming"].set_property("cmake_target_name", "ace+tao::TAO_CosNaming")
    self.cpp_info.components["TAO_CosNaming"].libs = ["TAO_CosNaming"]
    self.cpp_info.components["TAO_CosNaming"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosNaming_Serv"].set_property("cmake_target_name", "ace+tao::TAO_CosNaming_Serv")
    self.cpp_info.components["TAO_CosNaming_Serv"].libs = ["TAO_CosNaming_Serv"]
    self.cpp_info.components["TAO_CosNaming_Serv"].requires = ["TAO_CosNaming_Skel", "TAO_Messaging", "TAO_Svc_Utils", "TAO_IORTable"]
    self.cpp_info.components["TAO_CosNaming_Skel"].set_property("cmake_target_name", "ace+tao::TAO_CosNaming_Skel")
    self.cpp_info.components["TAO_CosNaming_Skel"].libs = ["TAO_CosNaming_Skel"]
    self.cpp_info.components["TAO_CosNaming_Skel"].requires = ["TAO_CosNaming", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosNotification"].set_property("cmake_target_name", "ace+tao::TAO_CosNotification")
    self.cpp_info.components["TAO_CosNotification"].libs = ["TAO_CosNotification"]
    self.cpp_info.components["TAO_CosNotification"].requires = ["TAO_CosEvent", "TAO"]
    self.cpp_info.components["TAO_CosNotification_Serv"].set_property("cmake_target_name", "ace+tao::TAO_CosNotification_Serv")
    self.cpp_info.components["TAO_CosNotification_Serv"].libs = ["TAO_CosNotification_Serv"]
    self.cpp_info.components["TAO_CosNotification_Serv"].requires = ["TAO_CosNotification_Skel", "TAO_Svc_Utils", "TAO_DynamicAny", "TAO_ETCL"]
    self.cpp_info.components["TAO_CosNotification_Skel"].set_property("cmake_target_name", "ace+tao::TAO_CosNotification_Skel")
    self.cpp_info.components["TAO_CosNotification_Skel"].libs = ["TAO_CosNotification_Skel"]
    self.cpp_info.components["TAO_CosNotification_Skel"].requires = ["TAO_CosNotification", "TAO_CosEvent_Skel", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosProperty"].set_property("cmake_target_name", "ace+tao::TAO_CosProperty")
    self.cpp_info.components["TAO_CosProperty"].libs = ["TAO_CosProperty"]
    self.cpp_info.components["TAO_CosProperty"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosProperty_Serv"].set_property("cmake_target_name", "ace+tao::TAO_CosProperty_Serv")
    self.cpp_info.components["TAO_CosProperty_Serv"].libs = ["TAO_CosProperty_Serv"]
    self.cpp_info.components["TAO_CosProperty_Serv"].requires = ["TAO_CosProperty_Skel"]
    self.cpp_info.components["TAO_CosProperty_Skel"].set_property("cmake_target_name", "ace+tao::TAO_CosProperty_Skel")
    self.cpp_info.components["TAO_CosProperty_Skel"].libs = ["TAO_CosProperty_Skel"]
    self.cpp_info.components["TAO_CosProperty_Skel"].requires = ["TAO_CosProperty", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosTime"].set_property("cmake_target_name", "ace+tao::TAO_CosTime")
    self.cpp_info.components["TAO_CosTime"].libs = ["TAO_CosTime"]
    self.cpp_info.components["TAO_CosTime"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosTime_Serv"].set_property("cmake_target_name", "ace+tao::TAO_CosTime_Serv")
    self.cpp_info.components["TAO_CosTime_Serv"].libs = ["TAO_CosTime_Serv"]
    self.cpp_info.components["TAO_CosTime_Serv"].requires = ["TAO_CosTime_Skel", "TAO_Svc_Utils"]
    self.cpp_info.components["TAO_CosTime_Skel"].set_property("cmake_target_name", "ace+tao::TAO_CosTime_Skel")
    self.cpp_info.components["TAO_CosTime_Skel"].libs = ["TAO_CosTime_Skel"]
    self.cpp_info.components["TAO_CosTime_Skel"].requires = ["TAO_CosTime", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosTrading"].set_property("cmake_target_name", "ace+tao::TAO_CosTrading")
    self.cpp_info.components["TAO_CosTrading"].libs = ["TAO_CosTrading"]
    self.cpp_info.components["TAO_CosTrading"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosTrading_Serv"].set_property("cmake_target_name", "ace+tao::TAO_CosTrading_Serv")
    self.cpp_info.components["TAO_CosTrading_Serv"].libs = ["TAO_CosTrading_Serv"]
    self.cpp_info.components["TAO_CosTrading_Serv"].requires = ["TAO_CosTrading_Skel", "TAO_Svc_Utils", "TAO_DynamicAny"]
    self.cpp_info.components["TAO_CosTrading_Skel"].set_property("cmake_target_name", "ace+tao::TAO_CosTrading_Skel")
    self.cpp_info.components["TAO_CosTrading_Skel"].libs = ["TAO_CosTrading_Skel"]
    self.cpp_info.components["TAO_CosTrading_Skel"].requires = ["TAO_CosTrading", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CSD_Framework"].set_property("cmake_target_name", "ace+tao::TAO_CSD_Framework")
    self.cpp_info.components["TAO_CSD_Framework"].libs = ["TAO_CSD_Framework"]
    self.cpp_info.components["TAO_CSD_Framework"].requires = ["TAO_PortableServer", "TAO_PI", "TAO"]
    self.cpp_info.components["TAO_CSD_ThreadPool"].set_property("cmake_target_name", "ace+tao::TAO_CSD_ThreadPool")
    self.cpp_info.components["TAO_CSD_ThreadPool"].libs = ["TAO_CSD_ThreadPool"]
    self.cpp_info.components["TAO_CSD_ThreadPool"].requires = ["TAO_CSD_Framework"]
    self.cpp_info.components["TAO_DiffServPolicy"].set_property("cmake_target_name", "ace+tao::TAO_DiffServPolicy")
    self.cpp_info.components["TAO_DiffServPolicy"].libs = ["TAO_DiffServPolicy"]
    self.cpp_info.components["TAO_DiffServPolicy"].requires = ["TAO_PI", "TAO_PortableServer", "TAO"]
    self.cpp_info.components["TAO_DsEventLogAdmin"].set_property("cmake_target_name", "ace+tao::TAO_DsEventLogAdmin")
    self.cpp_info.components["TAO_DsEventLogAdmin"].libs = ["TAO_DsEventLogAdmin"]
    self.cpp_info.components["TAO_DsEventLogAdmin"].requires = ["TAO", "TAO_DsLogAdmin", "TAO_CosEvent"]
    self.cpp_info.components["TAO_DsEventLogAdmin_Serv"].set_property("cmake_target_name", "ace+tao::TAO_DsEventLogAdmin_Serv")
    self.cpp_info.components["TAO_DsEventLogAdmin_Serv"].libs = ["TAO_DsEventLogAdmin_Serv"]
    self.cpp_info.components["TAO_DsEventLogAdmin_Serv"].requires = ["TAO_DsEventLogAdmin_Skel", "TAO_DsLogAdmin_Serv", "TAO_CosEvent_Serv"]
    self.cpp_info.components["TAO_DsEventLogAdmin_Skel"].set_property("cmake_target_name", "ace+tao::TAO_DsEventLogAdmin_Skel")
    self.cpp_info.components["TAO_DsEventLogAdmin_Skel"].libs = ["TAO_DsEventLogAdmin_Skel"]
    self.cpp_info.components["TAO_DsEventLogAdmin_Skel"].requires = ["TAO_DsEventLogAdmin", "TAO_DsLogAdmin_Skel", "TAO_CosEvent_Skel", "TAO_PortableServer"]
    self.cpp_info.components["TAO_DsLogAdmin"].set_property("cmake_target_name", "ace+tao::TAO_DsLogAdmin")
    self.cpp_info.components["TAO_DsLogAdmin"].libs = ["TAO_DsLogAdmin"]
    self.cpp_info.components["TAO_DsLogAdmin"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_DsLogAdmin_Serv"].set_property("cmake_target_name", "ace+tao::TAO_DsLogAdmin_Serv")
    self.cpp_info.components["TAO_DsLogAdmin_Serv"].libs = ["TAO_DsLogAdmin_Serv"]
    self.cpp_info.components["TAO_DsLogAdmin_Serv"].requires = ["TAO_DsLogAdmin_Skel", "TAO_DynamicAny", "TAO_ETCL", "TAO_Svc_Utils"]
    self.cpp_info.components["TAO_DsLogAdmin_Skel"].set_property("cmake_target_name", "ace+tao::TAO_DsLogAdmin_Skel")
    self.cpp_info.components["TAO_DsLogAdmin_Skel"].libs = ["TAO_DsLogAdmin_Skel"]
    self.cpp_info.components["TAO_DsLogAdmin_Skel"].requires = ["TAO_DsLogAdmin", "TAO_PortableServer"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin"].set_property("cmake_target_name", "ace+tao::TAO_DsNotifyLogAdmin")
    self.cpp_info.components["TAO_DsNotifyLogAdmin"].libs = ["TAO_DsNotifyLogAdmin"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin"].requires = ["TAO_DsEventLogAdmin", "TAO_DsLogAdmin", "TAO_CosNotification", "TAO_CosEvent", "TAO"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Serv"].set_property("cmake_target_name", "ace+tao::TAO_DsNotifyLogAdmin_Serv")
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Serv"].libs = ["TAO_DsNotifyLogAdmin_Serv"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Serv"].requires = ["TAO_DsNotifyLogAdmin_Skel", "TAO_DsLogAdmin_Serv"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Skel"].set_property("cmake_target_name", "ace+tao::TAO_DsNotifyLogAdmin_Skel")
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Skel"].libs = ["TAO_DsNotifyLogAdmin_Skel"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Skel"].requires = ["TAO_DsNotifyLogAdmin", "TAO_DsEventLogAdmin_Skel", "TAO_DsLogAdmin_Skel", "TAO_CosNotification_Skel", "TAO_CosEvent_Skel", "TAO_PortableServer"]
    self.cpp_info.components["TAO_DynamicAny"].set_property("cmake_target_name", "ace+tao::TAO_DynamicAny")
    self.cpp_info.components["TAO_DynamicAny"].libs = ["TAO_DynamicAny"]
    self.cpp_info.components["TAO_DynamicAny"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_DynamicInterface"].set_property("cmake_target_name", "ace+tao::TAO_DynamicInterface")
    self.cpp_info.components["TAO_DynamicInterface"].libs = ["TAO_DynamicInterface"]
    self.cpp_info.components["TAO_DynamicInterface"].requires = ["TAO_Messaging", "TAO_PI", "TAO_CodecFactory", "TAO_PortableServer", "TAO_Valuetype", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_EndpointPolicy"].set_property("cmake_target_name", "ace+tao::TAO_EndpointPolicy")
    self.cpp_info.components["TAO_EndpointPolicy"].libs = ["TAO_EndpointPolicy"]
    self.cpp_info.components["TAO_EndpointPolicy"].requires = ["TAO_PI", "TAO_PortableServer", "TAO"]
    self.cpp_info.components["TAO_ETCL"].set_property("cmake_target_name", "ace+tao::TAO_ETCL")
    self.cpp_info.components["TAO_ETCL"].libs = ["TAO_ETCL"]
    self.cpp_info.components["TAO_ETCL"].requires = ["ACE_ETCL"]
    self.cpp_info.components["TAO_FaultTolerance"].set_property("cmake_target_name", "ace+tao::TAO_FaultTolerance")
    self.cpp_info.components["TAO_FaultTolerance"].libs = ["TAO_FaultTolerance"]
    self.cpp_info.components["TAO_FaultTolerance"].requires = ["TAO_FT_ServerORB", "TAO_FT_ClientORB", "TAO_CosNotification"]
    self.cpp_info.components["TAO_FT_ClientORB"].set_property("cmake_target_name", "ace+tao::TAO_FT_ClientORB")
    self.cpp_info.components["TAO_FT_ClientORB"].libs = ["TAO_FT_ClientORB"]
    self.cpp_info.components["TAO_FT_ClientORB"].requires = ["TAO_FTORB_Utils", "TAO_Messaging", "TAO_PortableGroup"]
    self.cpp_info.components["TAO_FTORB_Utils"].set_property("cmake_target_name", "ace+tao::TAO_FTORB_Utils")
    self.cpp_info.components["TAO_FTORB_Utils"].libs = ["TAO_FTORB_Utils"]
    self.cpp_info.components["TAO_FTORB_Utils"].requires = ["TAO_IORManip", "TAO_PortableServer", "TAO"]
    self.cpp_info.components["TAO_FT_ServerORB"].set_property("cmake_target_name", "ace+tao::TAO_FT_ServerORB")
    self.cpp_info.components["TAO_FT_ServerORB"].libs = ["TAO_FT_ServerORB"]
    self.cpp_info.components["TAO_FT_ServerORB"].requires = ["TAO_FTORB_Utils", "TAO_Messaging", "TAO_PortableGroup"]
    self.cpp_info.components["TAO_IFR_Client"].set_property("cmake_target_name", "ace+tao::TAO_IFR_Client")
    self.cpp_info.components["TAO_IFR_Client"].libs = ["TAO_IFR_Client"]
    self.cpp_info.components["TAO_IFR_Client"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_ImR_Client"].set_property("cmake_target_name", "ace+tao::TAO_ImR_Client")
    self.cpp_info.components["TAO_ImR_Client"].libs = ["TAO_ImR_Client"]
    self.cpp_info.components["TAO_ImR_Client"].requires = ["TAO_PortableServer", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_IORInterceptor"].set_property("cmake_target_name", "ace+tao::TAO_IORInterceptor")
    self.cpp_info.components["TAO_IORInterceptor"].libs = ["TAO_IORInterceptor"]
    self.cpp_info.components["TAO_IORInterceptor"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_ObjRefTemplate", "TAO_Valuetype", "TAO_PortableServer", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_IORManip"].set_property("cmake_target_name", "ace+tao::TAO_IORManip")
    self.cpp_info.components["TAO_IORManip"].libs = ["TAO_IORManip"]
    self.cpp_info.components["TAO_IORManip"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_IORTable"].set_property("cmake_target_name", "ace+tao::TAO_IORTable")
    self.cpp_info.components["TAO_IORTable"].libs = ["TAO_IORTable"]
    self.cpp_info.components["TAO_IORTable"].requires = ["TAO"]
    self.cpp_info.components["TAO_Messaging"].set_property("cmake_target_name", "ace+tao::TAO_Messaging")
    self.cpp_info.components["TAO_Messaging"].libs = ["TAO_Messaging"]
    self.cpp_info.components["TAO_Messaging"].requires = ["TAO_Valuetype", "TAO_PI", "TAO_CodecFactory", "TAO_PortableServer", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Monitor"].set_property("cmake_target_name", "ace+tao::TAO_Monitor")
    self.cpp_info.components["TAO_Monitor"].libs = ["TAO_Monitor"]
    self.cpp_info.components["TAO_Monitor"].requires = ["TAO_PortableServer", "ACE_Monitor_Control"]
    self.cpp_info.components["TAO_ObjRefTemplate"].set_property("cmake_target_name", "ace+tao::TAO_ObjRefTemplate")
    self.cpp_info.components["TAO_ObjRefTemplate"].libs = ["TAO_ObjRefTemplate"]
    self.cpp_info.components["TAO_ObjRefTemplate"].requires = ["TAO_PortableServer", "TAO_Valuetype", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO"].set_property("cmake_target_name", "ace+tao::TAO")
    self.cpp_info.components["TAO"].libs = ["TAO"]
    self.cpp_info.components["TAO"].requires = ["ACE"]
    self.cpp_info.components["TAO_PI"].set_property("cmake_target_name", "ace+tao::TAO_PI")
    self.cpp_info.components["TAO_PI"].libs = ["TAO_PI"]
    self.cpp_info.components["TAO_PI"].requires = ["TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_PI_Server"].set_property("cmake_target_name", "ace+tao::TAO_PI_Server")
    self.cpp_info.components["TAO_PI_Server"].libs = ["TAO_PI_Server"]
    self.cpp_info.components["TAO_PI_Server"].requires = ["TAO_PortableServer", "TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_PortableGroup"].set_property("cmake_target_name", "ace+tao::TAO_PortableGroup")
    self.cpp_info.components["TAO_PortableGroup"].libs = ["TAO_PortableGroup"]
    self.cpp_info.components["TAO_PortableGroup"].requires = ["TAO_CosNaming", "TAO_IORManip", "TAO_Messaging", "TAO"]
    self.cpp_info.components["TAO_PortableServer"].set_property("cmake_target_name", "ace+tao::TAO_PortableServer")
    self.cpp_info.components["TAO_PortableServer"].libs = ["TAO_PortableServer"]
    self.cpp_info.components["TAO_PortableServer"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_RTCORBA"].set_property("cmake_target_name", "ace+tao::TAO_RTCORBA")
    self.cpp_info.components["TAO_RTCORBA"].libs = ["TAO_RTCORBA"]
    self.cpp_info.components["TAO_RTCORBA"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_RTEventLogAdmin"].set_property("cmake_target_name", "ace+tao::TAO_RTEventLogAdmin")
    self.cpp_info.components["TAO_RTEventLogAdmin"].libs = ["TAO_RTEventLogAdmin"]
    self.cpp_info.components["TAO_RTEventLogAdmin"].requires = ["TAO", "TAO_DsLogAdmin", "TAO_RTEvent"]
    self.cpp_info.components["TAO_RTEventLogAdmin_Serv"].set_property("cmake_target_name", "ace+tao::TAO_RTEventLogAdmin_Serv")
    self.cpp_info.components["TAO_RTEventLogAdmin_Serv"].libs = ["TAO_RTEventLogAdmin_Serv"]
    self.cpp_info.components["TAO_RTEventLogAdmin_Serv"].requires = ["TAO_RTEventLogAdmin_Skel", "TAO_DsLogAdmin_Serv", "TAO_RTEvent_Serv"]
    self.cpp_info.components["TAO_RTEventLogAdmin_Skel"].set_property("cmake_target_name", "ace+tao::TAO_RTEventLogAdmin_Skel")
    self.cpp_info.components["TAO_RTEventLogAdmin_Skel"].libs = ["TAO_RTEventLogAdmin_Skel"]
    self.cpp_info.components["TAO_RTEventLogAdmin_Skel"].requires = ["TAO_RTEventLogAdmin", "TAO_DsLogAdmin_Skel", "TAO_RTEvent_Skel", "TAO_PortableServer"]
    self.cpp_info.components["TAO_RTEvent"].set_property("cmake_target_name", "ace+tao::TAO_RTEvent")
    self.cpp_info.components["TAO_RTEvent"].libs = ["TAO_RTEvent"]
    self.cpp_info.components["TAO_RTEvent"].requires = ["TAO_Svc_Utils", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_RTEvent_Serv"].set_property("cmake_target_name", "ace+tao::TAO_RTEvent_Serv")
    self.cpp_info.components["TAO_RTEvent_Serv"].libs = ["TAO_RTEvent_Serv"]
    self.cpp_info.components["TAO_RTEvent_Serv"].requires = ["TAO_RTEvent_Skel", "TAO_Svc_Utils", "TAO_Messaging"]
    self.cpp_info.components["TAO_RTEvent_Skel"].set_property("cmake_target_name", "ace+tao::TAO_RTEvent_Skel")
    self.cpp_info.components["TAO_RTEvent_Skel"].libs = ["TAO_RTEvent_Skel"]
    self.cpp_info.components["TAO_RTEvent_Skel"].requires = ["TAO_RTEvent", "TAO_PortableServer"]
    self.cpp_info.components["TAO_RTPortableServer"].set_property("cmake_target_name", "ace+tao::TAO_RTPortableServer")
    self.cpp_info.components["TAO_RTPortableServer"].libs = ["TAO_RTPortableServer"]
    self.cpp_info.components["TAO_RTPortableServer"].requires = ["TAO_PortableServer", "TAO_RTCORBA", "TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_RTScheduler"].set_property("cmake_target_name", "ace+tao::TAO_RTScheduler")
    self.cpp_info.components["TAO_RTScheduler"].libs = ["TAO_RTScheduler"]
    self.cpp_info.components["TAO_RTScheduler"].requires = ["TAO_PI_Server", "TAO_PortableServer", "TAO_RTCORBA", "TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_SmartProxies"].set_property("cmake_target_name", "ace+tao::TAO_SmartProxies")
    self.cpp_info.components["TAO_SmartProxies"].libs = ["TAO_SmartProxies"]
    self.cpp_info.components["TAO_SmartProxies"].requires = ["TAO"]
    self.cpp_info.components["TAO_Strategies"].set_property("cmake_target_name", "ace+tao::TAO_Strategies")
    self.cpp_info.components["TAO_Strategies"].libs = ["TAO_Strategies"]
    self.cpp_info.components["TAO_Strategies"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Svc_Utils"].set_property("cmake_target_name", "ace+tao::TAO_Svc_Utils")
    self.cpp_info.components["TAO_Svc_Utils"].libs = ["TAO_Svc_Utils"]
    self.cpp_info.components["TAO_Svc_Utils"].requires = ["TAO_PortableServer"]
    self.cpp_info.components["TAO_TypeCodeFactory"].set_property("cmake_target_name", "ace+tao::TAO_TypeCodeFactory")
    self.cpp_info.components["TAO_TypeCodeFactory"].libs = ["TAO_TypeCodeFactory"]
    self.cpp_info.components["TAO_TypeCodeFactory"].requires = ["TAO_IFR_Client", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Utils"].set_property("cmake_target_name", "ace+tao::TAO_Utils")
    self.cpp_info.components["TAO_Utils"].libs = ["TAO_Utils"]
    self.cpp_info.components["TAO_Utils"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_PortableServer", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Valuetype"].set_property("cmake_target_name", "ace+tao::TAO_Valuetype")
    self.cpp_info.components["TAO_Valuetype"].libs = ["TAO_Valuetype"]
    self.cpp_info.components["TAO_Valuetype"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_ZIOP"].set_property("cmake_target_name", "ace+tao::TAO_ZIOP")
    self.cpp_info.components["TAO_ZIOP"].libs = ["TAO_ZIOP"]
    self.cpp_info.components["TAO_ZIOP"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    if self.options.with_zlib:
      self.cpp_info.components["TAO_ZlibCompressor"].set_property("cmake_target_name", "ace+tao::TAO_ZlibCompressor")
      self.cpp_info.components["TAO_ZlibCompressor"].libs = ["TAO_ZlibCompressor"]
      self.cpp_info.components["TAO_ZlibCompressor"].requires = ["TAO_Compression", "zlib::zlib"]
    self.output.info("Setting ACE_ROOT: {}".format(self.package_folder))
    self.runenv_info.define("ACE_ROOT", self.package_folder)
