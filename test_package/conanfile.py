#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self, generator='NMake Makefiles' if os.name == 'nt' else 'Unix Makefiles')
        cmake.configure()
        cmake.build()

    def test(self):
        with tools.environment_append(RunEnvironment(self).vars):
            with tools.chdir('bin'):
                node = 'node.exe' if os.name == 'nt' else 'node'
                # FIXME : hard-coded version of nodejs
                node = os.path.join(os.environ['EMSDK'], 'node', '8.9.1_64bit', 'bin', node)
                self.run('%s test_package.js' % node)
