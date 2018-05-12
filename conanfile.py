#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os
import shutil


class EmSDKInstallerConan(ConanFile):
    name = "emsdk_installer"
    version = "1.37.40"
    description = "Emscripten is an Open Source LLVM to JavaScript compiler"
    url = "https://github.com/bincrafters/conan-emsdk_installer"
    homepage = "https://github.com/kripken/emscripten"
    license = "MIT"
    exports = ["LICENSE.md"]

    settings = {
        "os_build": ['Windows', 'Linux', 'Macos'],
        "arch_build": ['x86_64'],
        "compiler": ['clang']
    }
    no_copy_source = True
    short_paths = True

    def source(self):
        source_url = 'https://github.com/juj/emsdk/archive/master.zip'
        tools.get(source_url)

    def build(self):
        with tools.chdir(os.path.join(self.source_folder, 'emsdk-master')):
            emsdk = 'emsdk.bat' if os.name == 'nt' else './emsdk'
            if os.name == 'posix':
                os.chmod('emsdk', os.stat('emsdk').st_mode | 0o111)
            self.run('%s update' % emsdk)
            self.run('%s install sdk-%s-64bit' % (emsdk, self.version))
            self.run('%s activate sdk-%s-64bit --embedded' % (emsdk, self.version))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_folder)
        src = os.path.join(self.source_folder, 'emsdk-master')
        dst = os.path.join(self.package_folder, 'e')
        if os.name == 'nt':
            src = '\\\\?\\' + os.path.abspath(src)
            dst = '\\\\?\\' + os.path.abspath(dst)
        if not os.path.isdir(dst):
            shutil.copytree(src, dst)

    def define_tool_var(self, name, value):
        suffix = '.bat' if os.name == 'nt' else ''
        path = os.path.join(self.package_folder, 'e', 'emscripten', self.version, '%s%s' % (value, suffix))
        self.output.info('Creating %s environment variable: %s' % (name, path))
        return path

    def package_info(self):
        emsdk = os.path.join(self.package_folder, 'e')
        em_config = os.path.join(emsdk, '.emscripten')
        emscripten = os.path.join(emsdk, 'emscripten', self.version)
        em_cache = os.path.join(emsdk, '.emscripten_cache')
        toolchain = os.path.join(emscripten, 'cmake', 'Modules', 'Platform', 'Emscripten.cmake')

        self.output.info('Appending PATH environment variable: %s' % emsdk)
        self.env_info.PATH.append(emsdk)

        self.output.info('Appending PATH environment variable: %s' % emscripten)
        self.env_info.PATH.append(emscripten)

        self.output.info('Creating EMSDK environment variable: %s' % emsdk)
        self.env_info.EMSDK = emsdk

        self.output.info('Creating EMSCRIPTEN environment variable: %s' % emscripten)
        self.env_info.EMSCRIPTEN = emscripten

        self.output.info('Creating EM_CONFIG environment variable: %s' % em_config)
        self.env_info.EM_CONFIG = em_config

        self.output.info('Creating EM_CACHE environment variable: %s' % em_cache)
        self.env_info.EM_CACHE = em_cache

        self.output.info('Creating CONAN_CMAKE_TOOLCHAIN_FILE environment variable: %s' % toolchain)
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain

        self.env_info.CC = self.define_tool_var('CC', 'emcc')
        self.env_info.CXX = self.define_tool_var('CXX', 'em++')
        self.env_info.RANLIB = self.define_tool_var('RANLIB', 'emranlib')
        self.env_info.AR = self.define_tool_var('AR', 'emar')
