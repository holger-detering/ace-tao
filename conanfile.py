from conans import ConanFile, AutoToolsBuildEnvironment, tools
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
  generators = "cmake"
  exports_sources = f"sources/ACE+TAO-src-{version}.tar.bz2"

  def _fetch_sources(self):
    tarball_name = f"ACE+TAO-src-{self.version}.tar.bz2"
    url = f"https://github.com/DOCGroup/ACE_TAO/releases/download/ACE%2BTAO-{self.version.replace('.', '_')}/" + tarball_name
    # url = f"http://localhost:5555/DOCGroup/ACE_TAO/releases/download/ACE%2BTAO-{self.version.replace('.', '_')}/" + tarball_name
    source_path = "sources/" + tarball_name
    checksums = self.conan_data["checksums"][self.version][0]
    if os.path.isfile(source_path):
      tools.check_md5(source_path, checksums["md5"])
      tools.unzip(source_path)
    else:
      tools.get(url, md5=checksums["md5"], verify=False)

  def source(self):
    self._fetch_sources()
    tools.save("ACE_wrappers/ace/config.h", """\
#include "ace/config-linux.h"
""")
    tools.save("ACE_wrappers/include/makeinclude/platform_macros.GNU", """\
include $(ACE_ROOT)/include/makeinclude/platform_linux.GNU
""")

  def requirements(self):
    if self.options.with_bzip2:
      self.requires("bzip2/1.0.8")
    if self.options.with_xerces:
      self.requires("xerces-c/3.2.2")
    if self.options.with_zlib:
      self.requires("zlib/1.2.11")

  def _get_make_options(self):
    options = []
    if self.options.with_bzip2:
      options.append("bzip2=1");
    if self.options.with_xerces:
      options.append("xerces=1");
    if self.options.with_zlib:
      options.append("zlib=1");
    if self.settings.build_type == "Debug" or self.settings.build_type == "RelWithDebInfo":
      options.append("debug=1");
    if self.settings.build_type == "Debug":
      options.append("optimize=0");
    return options

  def build(self):
    ace_root = f"{self.source_folder}/ACE_wrappers"
    tao_root = f"{ace_root}/TAO"
    features = ""
    if self.options.with_bzip2:
      features += "bzip2=1\n";
    if self.options.with_xerces:
      features += "xerces=1\n";
    if self.options.with_zlib:
      features += "zlib=1\n";
    with tools.environment_append({"ACE_ROOT": ace_root, "TAO_ROOT": tao_root}):
      with tools.chdir(ace_root):
        tools.save("MPC/config/default.features", features)
      with tools.chdir(tao_root):
        self.run("$ACE_ROOT/bin/mwc.pl TAO_ACE.mwc -type gnuace")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.make(self._get_make_options())

  def package(self):
    ace_root = f"{self.source_folder}/ACE_wrappers"
    tao_root = f"{ace_root}/TAO"
    with tools.environment_append({"ACE_ROOT": ace_root, "TAO_ROOT": tao_root, "INSTALL_PREFIX": self.package_folder}):
      with tools.chdir(tao_root):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.install(self._get_make_options())

  def package_info(self):
    self.cpp_info.names["cmake_find_package"] = "ace+tao"
    self.cpp_info.components["ACE_ETCL_Parser"].names["cmake_find_package"] = "ACE_ETCL_Parser"
    self.cpp_info.components["ACE_ETCL_Parser"].libs = ["ACE_ETCL_Parser"]
    self.cpp_info.components["ACE_ETCL_Parser"].requires = ["ACE_ETCL"]
    self.cpp_info.components["ACE_ETCL"].names["cmake_find_package"] = "ACE_ETCL"
    self.cpp_info.components["ACE_ETCL"].libs = ["ACE_ETCL"]
    self.cpp_info.components["ACE_ETCL"].requires = ["ACE"]
    self.cpp_info.components["ACE_HTBP"].names["cmake_find_package"] = "ACE_HTBP"
    self.cpp_info.components["ACE_HTBP"].libs = ["ACE_HTBP"]
    self.cpp_info.components["ACE_HTBP"].requires = ["ACE"]
    self.cpp_info.components["ACE_INet"].names["cmake_find_package"] = "ACE_INet"
    self.cpp_info.components["ACE_INet"].libs = ["ACE_INet"]
    self.cpp_info.components["ACE_INet"].requires = ["ACE"]
    self.cpp_info.components["ACE_Monitor_Control"].names["cmake_find_package"] = "ACE_Monitor_Control"
    self.cpp_info.components["ACE_Monitor_Control"].libs = ["ACE_Monitor_Control"]
    self.cpp_info.components["ACE_Monitor_Control"].requires = ["ACE_ETCL_Parser"]
    self.cpp_info.components["ACE"].names["cmake_find_package"] = "ACE"
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
    self.cpp_info.components["ACE_RMCast"].names["cmake_find_package"] = "ACE_RMCast"
    self.cpp_info.components["ACE_RMCast"].libs = ["ACE_RMCast"]
    self.cpp_info.components["ACE_RMCast"].requires = ["ACE"]
    self.cpp_info.components["ACE_TMCast"].names["cmake_find_package"] = "ACE_TMCast"
    self.cpp_info.components["ACE_TMCast"].libs = ["ACE_TMCast"]
    self.cpp_info.components["ACE_TMCast"].requires = ["ACE"]
    self.cpp_info.components["ACEXML_Parser"].names["cmake_find_package"] = "ACEXML_Parser"
    self.cpp_info.components["ACEXML_Parser"].libs = ["ACEXML_Parser"]
    self.cpp_info.components["ACEXML_Parser"].requires = ["ACEXML"]
    self.cpp_info.components["ACEXML"].names["cmake_find_package"] = "ACEXML"
    self.cpp_info.components["ACEXML"].libs = ["ACEXML"]
    self.cpp_info.components["ACEXML"].requires = ["ACE"]
    if self.options.with_xerces:
      self.cpp_info.components["ACE_XML_Utils"].names["cmake_find_package"] = "ACE_XML_Utils"
      self.cpp_info.components["ACE_XML_Utils"].libs = ["ACE_XML_Utils"]
      self.cpp_info.components["ACE_XML_Utils"].requires = ["ACE", "xerces-c::xerces-c"]
    self.cpp_info.components["ACEXML_XML_Svc_Conf_Parser"].names["cmake_find_package"] = "ACEXML_XML_Svc_Conf_Parser"
    self.cpp_info.components["ACEXML_XML_Svc_Conf_Parser"].libs = ["ACEXML_XML_Svc_Conf_Parser"]
    self.cpp_info.components["ACEXML_XML_Svc_Conf_Parser"].requires = ["ACEXML_Parser"]
    self.cpp_info.components["Kokyu"].names["cmake_find_package"] = "Kokyu"
    self.cpp_info.components["Kokyu"].libs = ["Kokyu"]
    self.cpp_info.components["Kokyu"].requires = ["ACE"]
    self.cpp_info.components["TAO_AnyTypeCode"].names["cmake_find_package"] = "TAO_AnyTypeCode"
    self.cpp_info.components["TAO_AnyTypeCode"].libs = ["TAO_AnyTypeCode"]
    self.cpp_info.components["TAO_AnyTypeCode"].requires = ["TAO"]
    self.cpp_info.components["TAO_Async_IORTable"].names["cmake_find_package"] = "TAO_Async_IORTable"
    self.cpp_info.components["TAO_Async_IORTable"].libs = ["TAO_Async_IORTable"]
    self.cpp_info.components["TAO_Async_IORTable"].requires = ["TAO", "TAO_IORTable"]
    self.cpp_info.components["TAO_BiDirGIOP"].names["cmake_find_package"] = "TAO_BiDirGIOP"
    self.cpp_info.components["TAO_BiDirGIOP"].libs = ["TAO_BiDirGIOP"]
    self.cpp_info.components["TAO_BiDirGIOP"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    if self.options.with_bzip2:
      self.cpp_info.components["TAO_Bzip2Compressor"].names["cmake_find_package"] = "TAO_Bzip2Compressor"
      self.cpp_info.components["TAO_Bzip2Compressor"].libs = ["TAO_Bzip2Compressor"]
      self.cpp_info.components["TAO_Bzip2Compressor"].requires = ["TAO_Compression", "bzip2::bzip2"]
    self.cpp_info.components["TAO_CodecFactory"].names["cmake_find_package"] = "TAO_CodecFactory"
    self.cpp_info.components["TAO_CodecFactory"].libs = ["TAO_CodecFactory"]
    self.cpp_info.components["TAO_CodecFactory"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Codeset"].names["cmake_find_package"] = "TAO_Codeset"
    self.cpp_info.components["TAO_Codeset"].libs = ["TAO_Codeset"]
    self.cpp_info.components["TAO_Codeset"].requires = ["TAO"]
    self.cpp_info.components["TAO_Compression"].names["cmake_find_package"] = "TAO_Compression"
    self.cpp_info.components["TAO_Compression"].libs = ["TAO_Compression"]
    self.cpp_info.components["TAO_Compression"].requires = ["TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosConcurrency"].names["cmake_find_package"] = "TAO_CosConcurrency"
    self.cpp_info.components["TAO_CosConcurrency"].libs = ["TAO_CosConcurrency"]
    self.cpp_info.components["TAO_CosConcurrency"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosConcurrency_Serv"].names["cmake_find_package"] = "TAO_CosConcurrency_Serv"
    self.cpp_info.components["TAO_CosConcurrency_Serv"].libs = ["TAO_CosConcurrency_Serv"]
    self.cpp_info.components["TAO_CosConcurrency_Serv"].requires = ["TAO_CosConcurrency_Skel"]
    self.cpp_info.components["TAO_CosConcurrency_Skel"].names["cmake_find_package"] = "TAO_CosConcurrency_Skel"
    self.cpp_info.components["TAO_CosConcurrency_Skel"].libs = ["TAO_CosConcurrency_Skel"]
    self.cpp_info.components["TAO_CosConcurrency_Skel"].requires = ["TAO_CosConcurrency", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosEvent"].names["cmake_find_package"] = "TAO_CosEvent"
    self.cpp_info.components["TAO_CosEvent"].libs = ["TAO_CosEvent"]
    self.cpp_info.components["TAO_CosEvent"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosEvent_Serv"].names["cmake_find_package"] = "TAO_CosEvent_Serv"
    self.cpp_info.components["TAO_CosEvent_Serv"].libs = ["TAO_CosEvent_Serv"]
    self.cpp_info.components["TAO_CosEvent_Serv"].requires = ["TAO_CosEvent_Skel", "TAO_DynamicInterface", "TAO_IFR_Client", "TAO_Messaging", "TAO_CosNaming", "TAO_Svc_Utils"]
    self.cpp_info.components["TAO_CosEvent_Skel"].names["cmake_find_package"] = "TAO_CosEvent_Skel"
    self.cpp_info.components["TAO_CosEvent_Skel"].libs = ["TAO_CosEvent_Skel"]
    self.cpp_info.components["TAO_CosEvent_Skel"].requires = ["TAO_CosEvent", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosLifeCycle"].names["cmake_find_package"] = "TAO_CosLifeCycle"
    self.cpp_info.components["TAO_CosLifeCycle"].libs = ["TAO_CosLifeCycle"]
    self.cpp_info.components["TAO_CosLifeCycle"].requires = ["TAO_CosNaming", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosLifeCycle_Skel"].names["cmake_find_package"] = "TAO_CosLifeCycle_Skel"
    self.cpp_info.components["TAO_CosLifeCycle_Skel"].libs = ["TAO_CosLifeCycle_Skel"]
    self.cpp_info.components["TAO_CosLifeCycle_Skel"].requires = ["TAO_CosLifeCycle", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosLoadBalancing"].names["cmake_find_package"] = "TAO_CosLoadBalancing"
    self.cpp_info.components["TAO_CosLoadBalancing"].libs = ["TAO_CosLoadBalancing"]
    self.cpp_info.components["TAO_CosLoadBalancing"].requires = ["TAO_CosNaming", "TAO_IORManip", "TAO_PortableGroup", "TAO"]
    self.cpp_info.components["TAO_CosNaming"].names["cmake_find_package"] = "TAO_CosNaming"
    self.cpp_info.components["TAO_CosNaming"].libs = ["TAO_CosNaming"]
    self.cpp_info.components["TAO_CosNaming"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosNaming_Serv"].names["cmake_find_package"] = "TAO_CosNaming_Serv"
    self.cpp_info.components["TAO_CosNaming_Serv"].libs = ["TAO_CosNaming_Serv"]
    self.cpp_info.components["TAO_CosNaming_Serv"].requires = ["TAO_CosNaming_Skel", "TAO_Messaging", "TAO_Svc_Utils", "TAO_IORTable"]
    self.cpp_info.components["TAO_CosNaming_Skel"].names["cmake_find_package"] = "TAO_CosNaming_Skel"
    self.cpp_info.components["TAO_CosNaming_Skel"].libs = ["TAO_CosNaming_Skel"]
    self.cpp_info.components["TAO_CosNaming_Skel"].requires = ["TAO_CosNaming", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosNotification"].names["cmake_find_package"] = "TAO_CosNotification"
    self.cpp_info.components["TAO_CosNotification"].libs = ["TAO_CosNotification"]
    self.cpp_info.components["TAO_CosNotification"].requires = ["TAO_CosEvent", "TAO"]
    self.cpp_info.components["TAO_CosNotification_Serv"].names["cmake_find_package"] = "TAO_CosNotification_Serv"
    self.cpp_info.components["TAO_CosNotification_Serv"].libs = ["TAO_CosNotification_Serv"]
    self.cpp_info.components["TAO_CosNotification_Serv"].requires = ["TAO_CosNotification_Skel", "TAO_Svc_Utils", "TAO_DynamicAny", "TAO_ETCL"]
    self.cpp_info.components["TAO_CosNotification_Skel"].names["cmake_find_package"] = "TAO_CosNotification_Skel"
    self.cpp_info.components["TAO_CosNotification_Skel"].libs = ["TAO_CosNotification_Skel"]
    self.cpp_info.components["TAO_CosNotification_Skel"].requires = ["TAO_CosNotification", "TAO_CosEvent_Skel", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosProperty"].names["cmake_find_package"] = "TAO_CosProperty"
    self.cpp_info.components["TAO_CosProperty"].libs = ["TAO_CosProperty"]
    self.cpp_info.components["TAO_CosProperty"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosProperty_Serv"].names["cmake_find_package"] = "TAO_CosProperty_Serv"
    self.cpp_info.components["TAO_CosProperty_Serv"].libs = ["TAO_CosProperty_Serv"]
    self.cpp_info.components["TAO_CosProperty_Serv"].requires = ["TAO_CosProperty_Skel"]
    self.cpp_info.components["TAO_CosProperty_Skel"].names["cmake_find_package"] = "TAO_CosProperty_Skel"
    self.cpp_info.components["TAO_CosProperty_Skel"].libs = ["TAO_CosProperty_Skel"]
    self.cpp_info.components["TAO_CosProperty_Skel"].requires = ["TAO_CosProperty", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosTime"].names["cmake_find_package"] = "TAO_CosTime"
    self.cpp_info.components["TAO_CosTime"].libs = ["TAO_CosTime"]
    self.cpp_info.components["TAO_CosTime"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosTime_Serv"].names["cmake_find_package"] = "TAO_CosTime_Serv"
    self.cpp_info.components["TAO_CosTime_Serv"].libs = ["TAO_CosTime_Serv"]
    self.cpp_info.components["TAO_CosTime_Serv"].requires = ["TAO_CosTime_Skel", "TAO_Svc_Utils"]
    self.cpp_info.components["TAO_CosTime_Skel"].names["cmake_find_package"] = "TAO_CosTime_Skel"
    self.cpp_info.components["TAO_CosTime_Skel"].libs = ["TAO_CosTime_Skel"]
    self.cpp_info.components["TAO_CosTime_Skel"].requires = ["TAO_CosTime", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CosTrading"].names["cmake_find_package"] = "TAO_CosTrading"
    self.cpp_info.components["TAO_CosTrading"].libs = ["TAO_CosTrading"]
    self.cpp_info.components["TAO_CosTrading"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_CosTrading_Serv"].names["cmake_find_package"] = "TAO_CosTrading_Serv"
    self.cpp_info.components["TAO_CosTrading_Serv"].libs = ["TAO_CosTrading_Serv"]
    self.cpp_info.components["TAO_CosTrading_Serv"].requires = ["TAO_CosTrading_Skel", "TAO_Svc_Utils", "TAO_DynamicAny"]
    self.cpp_info.components["TAO_CosTrading_Skel"].names["cmake_find_package"] = "TAO_CosTrading_Skel"
    self.cpp_info.components["TAO_CosTrading_Skel"].libs = ["TAO_CosTrading_Skel"]
    self.cpp_info.components["TAO_CosTrading_Skel"].requires = ["TAO_CosTrading", "TAO_PortableServer"]
    self.cpp_info.components["TAO_CSD_Framework"].names["cmake_find_package"] = "TAO_CSD_Framework"
    self.cpp_info.components["TAO_CSD_Framework"].libs = ["TAO_CSD_Framework"]
    self.cpp_info.components["TAO_CSD_Framework"].requires = ["TAO_PortableServer", "TAO_PI", "TAO"]
    self.cpp_info.components["TAO_CSD_ThreadPool"].names["cmake_find_package"] = "TAO_CSD_ThreadPool"
    self.cpp_info.components["TAO_CSD_ThreadPool"].libs = ["TAO_CSD_ThreadPool"]
    self.cpp_info.components["TAO_CSD_ThreadPool"].requires = ["TAO_CSD_Framework"]
    self.cpp_info.components["TAO_DiffServPolicy"].names["cmake_find_package"] = "TAO_DiffServPolicy"
    self.cpp_info.components["TAO_DiffServPolicy"].libs = ["TAO_DiffServPolicy"]
    self.cpp_info.components["TAO_DiffServPolicy"].requires = ["TAO_PI", "TAO_PortableServer", "TAO"]
    self.cpp_info.components["TAO_DsEventLogAdmin"].names["cmake_find_package"] = "TAO_DsEventLogAdmin"
    self.cpp_info.components["TAO_DsEventLogAdmin"].libs = ["TAO_DsEventLogAdmin"]
    self.cpp_info.components["TAO_DsEventLogAdmin"].requires = ["TAO", "TAO_DsLogAdmin", "TAO_CosEvent"]
    self.cpp_info.components["TAO_DsEventLogAdmin_Serv"].names["cmake_find_package"] = "TAO_DsEventLogAdmin_Serv"
    self.cpp_info.components["TAO_DsEventLogAdmin_Serv"].libs = ["TAO_DsEventLogAdmin_Serv"]
    self.cpp_info.components["TAO_DsEventLogAdmin_Serv"].requires = ["TAO_DsEventLogAdmin_Skel", "TAO_DsLogAdmin_Serv", "TAO_CosEvent_Serv"]
    self.cpp_info.components["TAO_DsEventLogAdmin_Skel"].names["cmake_find_package"] = "TAO_DsEventLogAdmin_Skel"
    self.cpp_info.components["TAO_DsEventLogAdmin_Skel"].libs = ["TAO_DsEventLogAdmin_Skel"]
    self.cpp_info.components["TAO_DsEventLogAdmin_Skel"].requires = ["TAO_DsEventLogAdmin", "TAO_DsLogAdmin_Skel", "TAO_CosEvent_Skel", "TAO_PortableServer"]
    self.cpp_info.components["TAO_DsLogAdmin"].names["cmake_find_package"] = "TAO_DsLogAdmin"
    self.cpp_info.components["TAO_DsLogAdmin"].libs = ["TAO_DsLogAdmin"]
    self.cpp_info.components["TAO_DsLogAdmin"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_DsLogAdmin_Serv"].names["cmake_find_package"] = "TAO_DsLogAdmin_Serv"
    self.cpp_info.components["TAO_DsLogAdmin_Serv"].libs = ["TAO_DsLogAdmin_Serv"]
    self.cpp_info.components["TAO_DsLogAdmin_Serv"].requires = ["TAO_DsLogAdmin_Skel", "TAO_DynamicAny", "TAO_ETCL", "TAO_Svc_Utils"]
    self.cpp_info.components["TAO_DsLogAdmin_Skel"].names["cmake_find_package"] = "TAO_DsLogAdmin_Skel"
    self.cpp_info.components["TAO_DsLogAdmin_Skel"].libs = ["TAO_DsLogAdmin_Skel"]
    self.cpp_info.components["TAO_DsLogAdmin_Skel"].requires = ["TAO_DsLogAdmin", "TAO_PortableServer"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin"].names["cmake_find_package"] = "TAO_DsNotifyLogAdmin"
    self.cpp_info.components["TAO_DsNotifyLogAdmin"].libs = ["TAO_DsNotifyLogAdmin"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin"].requires = ["TAO_DsEventLogAdmin", "TAO_DsLogAdmin", "TAO_CosNotification", "TAO_CosEvent", "TAO"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Serv"].names["cmake_find_package"] = "TAO_DsNotifyLogAdmin_Serv"
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Serv"].libs = ["TAO_DsNotifyLogAdmin_Serv"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Serv"].requires = ["TAO_DsNotifyLogAdmin_Skel", "TAO_DsLogAdmin_Serv"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Skel"].names["cmake_find_package"] = "TAO_DsNotifyLogAdmin_Skel"
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Skel"].libs = ["TAO_DsNotifyLogAdmin_Skel"]
    self.cpp_info.components["TAO_DsNotifyLogAdmin_Skel"].requires = ["TAO_DsNotifyLogAdmin", "TAO_DsEventLogAdmin_Skel", "TAO_DsLogAdmin_Skel", "TAO_CosNotification_Skel", "TAO_CosEvent_Skel", "TAO_PortableServer"]
    self.cpp_info.components["TAO_DynamicAny"].names["cmake_find_package"] = "TAO_DynamicAny"
    self.cpp_info.components["TAO_DynamicAny"].libs = ["TAO_DynamicAny"]
    self.cpp_info.components["TAO_DynamicAny"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_DynamicInterface"].names["cmake_find_package"] = "TAO_DynamicInterface"
    self.cpp_info.components["TAO_DynamicInterface"].libs = ["TAO_DynamicInterface"]
    self.cpp_info.components["TAO_DynamicInterface"].requires = ["TAO_Messaging", "TAO_PI", "TAO_CodecFactory", "TAO_PortableServer", "TAO_Valuetype", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_EndpointPolicy"].names["cmake_find_package"] = "TAO_EndpointPolicy"
    self.cpp_info.components["TAO_EndpointPolicy"].libs = ["TAO_EndpointPolicy"]
    self.cpp_info.components["TAO_EndpointPolicy"].requires = ["TAO_PI", "TAO_PortableServer", "TAO"]
    self.cpp_info.components["TAO_ETCL"].names["cmake_find_package"] = "TAO_ETCL"
    self.cpp_info.components["TAO_ETCL"].libs = ["TAO_ETCL"]
    self.cpp_info.components["TAO_ETCL"].requires = ["ACE_ETCL"]
    self.cpp_info.components["TAO_FaultTolerance"].names["cmake_find_package"] = "TAO_FaultTolerance"
    self.cpp_info.components["TAO_FaultTolerance"].libs = ["TAO_FaultTolerance"]
    self.cpp_info.components["TAO_FaultTolerance"].requires = ["TAO_FT_ServerORB", "TAO_FT_ClientORB", "TAO_CosNotification"]
    self.cpp_info.components["TAO_FT_ClientORB"].names["cmake_find_package"] = "TAO_FT_ClientORB"
    self.cpp_info.components["TAO_FT_ClientORB"].libs = ["TAO_FT_ClientORB"]
    self.cpp_info.components["TAO_FT_ClientORB"].requires = ["TAO_FTORB_Utils", "TAO_Messaging", "TAO_PortableGroup"]
    self.cpp_info.components["TAO_FTORB_Utils"].names["cmake_find_package"] = "TAO_FTORB_Utils"
    self.cpp_info.components["TAO_FTORB_Utils"].libs = ["TAO_FTORB_Utils"]
    self.cpp_info.components["TAO_FTORB_Utils"].requires = ["TAO_IORManip", "TAO_PortableServer", "TAO"]
    self.cpp_info.components["TAO_FT_ServerORB"].names["cmake_find_package"] = "TAO_FT_ServerORB"
    self.cpp_info.components["TAO_FT_ServerORB"].libs = ["TAO_FT_ServerORB"]
    self.cpp_info.components["TAO_FT_ServerORB"].requires = ["TAO_FTORB_Utils", "TAO_Messaging", "TAO_PortableGroup"]
    self.cpp_info.components["TAO_IFR_Client"].names["cmake_find_package"] = "TAO_IFR_Client"
    self.cpp_info.components["TAO_IFR_Client"].libs = ["TAO_IFR_Client"]
    self.cpp_info.components["TAO_IFR_Client"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_ImR_Client"].names["cmake_find_package"] = "TAO_ImR_Client"
    self.cpp_info.components["TAO_ImR_Client"].libs = ["TAO_ImR_Client"]
    self.cpp_info.components["TAO_ImR_Client"].requires = ["TAO_PortableServer", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_IORInterceptor"].names["cmake_find_package"] = "TAO_IORInterceptor"
    self.cpp_info.components["TAO_IORInterceptor"].libs = ["TAO_IORInterceptor"]
    self.cpp_info.components["TAO_IORInterceptor"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_ObjRefTemplate", "TAO_Valuetype", "TAO_PortableServer", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_IORManip"].names["cmake_find_package"] = "TAO_IORManip"
    self.cpp_info.components["TAO_IORManip"].libs = ["TAO_IORManip"]
    self.cpp_info.components["TAO_IORManip"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_IORTable"].names["cmake_find_package"] = "TAO_IORTable"
    self.cpp_info.components["TAO_IORTable"].libs = ["TAO_IORTable"]
    self.cpp_info.components["TAO_IORTable"].requires = ["TAO"]
    self.cpp_info.components["TAO_Messaging"].names["cmake_find_package"] = "TAO_Messaging"
    self.cpp_info.components["TAO_Messaging"].libs = ["TAO_Messaging"]
    self.cpp_info.components["TAO_Messaging"].requires = ["TAO_Valuetype", "TAO_PI", "TAO_CodecFactory", "TAO_PortableServer", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Monitor"].names["cmake_find_package"] = "TAO_Monitor"
    self.cpp_info.components["TAO_Monitor"].libs = ["TAO_Monitor"]
    self.cpp_info.components["TAO_Monitor"].requires = ["TAO_PortableServer", "ACE_Monitor_Control"]
    self.cpp_info.components["TAO_ObjRefTemplate"].names["cmake_find_package"] = "TAO_ObjRefTemplate"
    self.cpp_info.components["TAO_ObjRefTemplate"].libs = ["TAO_ObjRefTemplate"]
    self.cpp_info.components["TAO_ObjRefTemplate"].requires = ["TAO_PortableServer", "TAO_Valuetype", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO"].names["cmake_find_package"] = "TAO"
    self.cpp_info.components["TAO"].libs = ["TAO"]
    self.cpp_info.components["TAO"].requires = ["ACE"]
    self.cpp_info.components["TAO_PI"].names["cmake_find_package"] = "TAO_PI"
    self.cpp_info.components["TAO_PI"].libs = ["TAO_PI"]
    self.cpp_info.components["TAO_PI"].requires = ["TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_PI_Server"].names["cmake_find_package"] = "TAO_PI_Server"
    self.cpp_info.components["TAO_PI_Server"].libs = ["TAO_PI_Server"]
    self.cpp_info.components["TAO_PI_Server"].requires = ["TAO_PortableServer", "TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_PortableGroup"].names["cmake_find_package"] = "TAO_PortableGroup"
    self.cpp_info.components["TAO_PortableGroup"].libs = ["TAO_PortableGroup"]
    self.cpp_info.components["TAO_PortableGroup"].requires = ["TAO_CosNaming", "TAO_IORManip", "TAO_Messaging", "TAO"]
    self.cpp_info.components["TAO_PortableServer"].names["cmake_find_package"] = "TAO_PortableServer"
    self.cpp_info.components["TAO_PortableServer"].libs = ["TAO_PortableServer"]
    self.cpp_info.components["TAO_PortableServer"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_RTCORBA"].names["cmake_find_package"] = "TAO_RTCORBA"
    self.cpp_info.components["TAO_RTCORBA"].libs = ["TAO_RTCORBA"]
    self.cpp_info.components["TAO_RTCORBA"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_RTEventLogAdmin"].names["cmake_find_package"] = "TAO_RTEventLogAdmin"
    self.cpp_info.components["TAO_RTEventLogAdmin"].libs = ["TAO_RTEventLogAdmin"]
    self.cpp_info.components["TAO_RTEventLogAdmin"].requires = ["TAO", "TAO_DsLogAdmin", "TAO_RTEvent"]
    self.cpp_info.components["TAO_RTEventLogAdmin_Serv"].names["cmake_find_package"] = "TAO_RTEventLogAdmin_Serv"
    self.cpp_info.components["TAO_RTEventLogAdmin_Serv"].libs = ["TAO_RTEventLogAdmin_Serv"]
    self.cpp_info.components["TAO_RTEventLogAdmin_Serv"].requires = ["TAO_RTEventLogAdmin_Skel", "TAO_DsLogAdmin_Serv", "TAO_RTEvent_Serv"]
    self.cpp_info.components["TAO_RTEventLogAdmin_Skel"].names["cmake_find_package"] = "TAO_RTEventLogAdmin_Skel"
    self.cpp_info.components["TAO_RTEventLogAdmin_Skel"].libs = ["TAO_RTEventLogAdmin_Skel"]
    self.cpp_info.components["TAO_RTEventLogAdmin_Skel"].requires = ["TAO_RTEventLogAdmin", "TAO_DsLogAdmin_Skel", "TAO_RTEvent_Skel", "TAO_PortableServer"]
    self.cpp_info.components["TAO_RTEvent"].names["cmake_find_package"] = "TAO_RTEvent"
    self.cpp_info.components["TAO_RTEvent"].libs = ["TAO_RTEvent"]
    self.cpp_info.components["TAO_RTEvent"].requires = ["TAO_Svc_Utils", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_RTEvent_Serv"].names["cmake_find_package"] = "TAO_RTEvent_Serv"
    self.cpp_info.components["TAO_RTEvent_Serv"].libs = ["TAO_RTEvent_Serv"]
    self.cpp_info.components["TAO_RTEvent_Serv"].requires = ["TAO_RTEvent_Skel", "TAO_Svc_Utils", "TAO_Messaging"]
    self.cpp_info.components["TAO_RTEvent_Skel"].names["cmake_find_package"] = "TAO_RTEvent_Skel"
    self.cpp_info.components["TAO_RTEvent_Skel"].libs = ["TAO_RTEvent_Skel"]
    self.cpp_info.components["TAO_RTEvent_Skel"].requires = ["TAO_RTEvent", "TAO_PortableServer"]
    self.cpp_info.components["TAO_RTPortableServer"].names["cmake_find_package"] = "TAO_RTPortableServer"
    self.cpp_info.components["TAO_RTPortableServer"].libs = ["TAO_RTPortableServer"]
    self.cpp_info.components["TAO_RTPortableServer"].requires = ["TAO_PortableServer", "TAO_RTCORBA", "TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_RTScheduler"].names["cmake_find_package"] = "TAO_RTScheduler"
    self.cpp_info.components["TAO_RTScheduler"].libs = ["TAO_RTScheduler"]
    self.cpp_info.components["TAO_RTScheduler"].requires = ["TAO_PI_Server", "TAO_PortableServer", "TAO_RTCORBA", "TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_SmartProxies"].names["cmake_find_package"] = "TAO_SmartProxies"
    self.cpp_info.components["TAO_SmartProxies"].libs = ["TAO_SmartProxies"]
    self.cpp_info.components["TAO_SmartProxies"].requires = ["TAO"]
    self.cpp_info.components["TAO_Strategies"].names["cmake_find_package"] = "TAO_Strategies"
    self.cpp_info.components["TAO_Strategies"].libs = ["TAO_Strategies"]
    self.cpp_info.components["TAO_Strategies"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Svc_Utils"].names["cmake_find_package"] = "TAO_Svc_Utils"
    self.cpp_info.components["TAO_Svc_Utils"].libs = ["TAO_Svc_Utils"]
    self.cpp_info.components["TAO_Svc_Utils"].requires = ["TAO_PortableServer"]
    self.cpp_info.components["TAO_TypeCodeFactory"].names["cmake_find_package"] = "TAO_TypeCodeFactory"
    self.cpp_info.components["TAO_TypeCodeFactory"].libs = ["TAO_TypeCodeFactory"]
    self.cpp_info.components["TAO_TypeCodeFactory"].requires = ["TAO_IFR_Client", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Utils"].names["cmake_find_package"] = "TAO_Utils"
    self.cpp_info.components["TAO_Utils"].libs = ["TAO_Utils"]
    self.cpp_info.components["TAO_Utils"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_PortableServer", "TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_Valuetype"].names["cmake_find_package"] = "TAO_Valuetype"
    self.cpp_info.components["TAO_Valuetype"].libs = ["TAO_Valuetype"]
    self.cpp_info.components["TAO_Valuetype"].requires = ["TAO_AnyTypeCode", "TAO"]
    self.cpp_info.components["TAO_ZIOP"].names["cmake_find_package"] = "TAO_ZIOP"
    self.cpp_info.components["TAO_ZIOP"].libs = ["TAO_ZIOP"]
    self.cpp_info.components["TAO_ZIOP"].requires = ["TAO_PI", "TAO_CodecFactory", "TAO_AnyTypeCode", "TAO"]
    if self.options.with_zlib:
      self.cpp_info.components["TAO_ZlibCompressor"].names["cmake_find_package"] = "TAO_ZlibCompressor"
      self.cpp_info.components["TAO_ZlibCompressor"].libs = ["TAO_ZlibCompressor"]
      self.cpp_info.components["TAO_ZlibCompressor"].requires = ["TAO_Compression", "zlib::zlib"]
    bin_path = os.path.join(self.package_folder, "bin")
    self.output.info("Appending PATH environment variable: {}".format(bin_path))
    self.env_info.PATH.append(bin_path)
    lib_path = os.path.join(self.package_folder, "lib")
    self.output.info("Appending LD_LIBRARY_PATH environment variable: {}".format(lib_path))
    self.env_info.LD_LIBRARY_PATH.append(lib_path)
    self.output.info("Setting ACE_ROOT: {}".format(self.package_folder))
    self.env_info.ACE_ROOT = self.package_folder
