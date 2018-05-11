#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
import platform
import os


if __name__ == "__main__":

    builder = build_template_default.get_builder()
    builder.builds = []

    settings = dict()
    settings['compiler'] = 'clang'
    settings['compiler.version'] = '5.0'
    settings['compiler.libcxx'] = 'libc++'
    settings['arch_build'] = 'x86_64'

    if platform.system() == 'Windows':
        settings['os_build'] = 'Windows'
    elif platform.system() == 'Linux':
        settings['os_build'] = 'Linux'
    elif platform.system() == 'Darwin':
        settings['os_build'] = 'Macos'

    builder.add(settings=settings.copy(), options={}, env_vars={}, build_requires={})

    builder.run()
