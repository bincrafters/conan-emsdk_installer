from conans import ConanFile, tools
import os


class EmSDKInstallerConan(ConanFile):
    name = "emsdk_installer"
    version = "1.39.6"
    description = "Emscripten is an Open Source LLVM to JavaScript compiler"
    url = "https://github.com/bincrafters/conan-emsdk_installer"
    homepage = "https://github.com/kripken/emscripten"
    topcis = ("conan", "emsdk", "emscripten", "installer", "sdk")
    license = "MIT"

    settings = {
        "os_build": ['Windows', 'Linux', 'Macos'],
        "arch_build": ['x86_64'],
    }
    short_paths = True
    requires = "nodejs_installer/10.15.0@bincrafters/stable"
    _source_subfolder = "source_subfolder"

    def source(self):
        commit = "997b0a19ff6fdfe0be8b966e1fed05bf5ebf85e4"
        sha256 = "f8043866f287176ec92a686ea2357ec13c80f6bc781999e1d0130b95ae97f0df"
        source_url = 'https://github.com/emscripten-core/emsdk/archive/%s.tar.gz' % commit
        tools.get(source_url, sha256=sha256)
        extracted_folder = "emsdk-%s" % commit
        os.rename(extracted_folder, self._source_subfolder)

    def _run(self, command):
        self.output.info(command)
        self.run(command)

    @staticmethod
    def _create_dummy_file(directory):
        if not os.path.isdir(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, "dummy"), "w") as f:
            f.write("\n")

    @staticmethod
    def _touch(filename):
        if not os.path.isfile(filename):
            with open(filename, "w") as f:
                f.write("\n")

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def build(self):
        with tools.chdir(self._source_subfolder):
            emsdk = 'emsdk.bat' if os.name == 'nt' else './emsdk'
            if os.path.isfile("python_selector"):
                self._chmod_plus_x("python_selector")
            self._chmod_plus_x('emsdk')
            self._run('%s update' % emsdk)
            if os.path.isfile("python_selector"):
                self._chmod_plus_x("python_selector")
            self._chmod_plus_x('emsdk')

            # skip undesired installation of tools (nodejs, java, python)
            # FIXME: if someone knows easier way to skip installation of tools, please tell me
            self._create_dummy_file(os.path.join("node", "8.9.1_64bit"))
            self._create_dummy_file(os.path.join("java", "8.152_64bit"))
            if not os.path.isdir("zips"):
                os.makedirs("zips")
            platform = {"Macos": "darwin",
                        "Windows": "win",
                        "Linux": "linux"}.get(str(self.settings.os_build))
            ext = {"Macos": "tar.gz",
                   "Linux": "tar.xz",
                   "Windows": "zip"}.get(str(self.settings.os_build))
            self._touch(os.path.join("zips", "node-v8.9.1-%s-x64.%s" % (platform, ext)))
            self._run('%s list' % emsdk)
            self._run('%s install %s' % (emsdk, self.version))
            self._run('%s activate %s --embedded' % (emsdk, self.version))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern='*', dst='.', src=self._source_subfolder)
        emsdk = self.package_folder
        emscripten = os.path.join(emsdk, 'upstream', 'emscripten')
        toolchain = os.path.join(emscripten, 'cmake', 'Modules', 'Platform', 'Emscripten.cmake')
        # allow to find conan libraries
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)")
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)")
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)")

    def _define_tool_var(self, name, value):
        suffix = '.bat' if os.name == 'nt' else ''
        path = os.path.join(self.package_folder, 'upstream', 'emscripten', '%s%s' % (value, suffix))
        self._chmod_plus_x(path)
        self.output.info('Creating %s environment variable: %s' % (name, path))
        return path

    def package_info(self):
        emsdk = self.package_folder
        em_config = os.path.join(emsdk, '.emscripten')
        emscripten = os.path.join(emsdk, 'upstream', 'emscripten')
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

        self.env_info.CC = self._define_tool_var('CC', 'emcc')
        self.env_info.CXX = self._define_tool_var('CXX', 'em++')
        self.env_info.RANLIB = self._define_tool_var('RANLIB', 'emranlib')
        self.env_info.AR = self._define_tool_var('AR', 'emar')
