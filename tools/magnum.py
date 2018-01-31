#! /usr/bin/env python
# encoding: utf-8
# Konstantinos Chatzilygeroudis - 2018

"""
Quick n dirty Magnum detection
"""

import os
import re
from waflib import Utils, Logs
from waflib.Configure import conf
# import corrade
import copy

def options(opt):
        # opt.load('corrade')
        opt.add_option('--magnum_install_dir', type='string', help='path to magnum install directory', dest='magnum_install_dir')

@conf
def check_magnum(conf, *k, **kw):
    # conf.load('corrade')

    def get_directory(filename, dirs, full = False):
        res = conf.find_file(filename, dirs)
        if not full:
            return res[:-len(filename)-1]
        return res[:res.rfind('/')]
    def find_in_string(data, text):
        return data.find(text)

    # Check compiler version (for gcc); I am being a bit more strong (Magnum could be built with 4.7 but needs adjustment)
    if conf.env.CXX_NAME in ["gcc", "g++"] and int(conf.env['CC_VERSION'][0]+conf.env['CC_VERSION'][1]) < 48:
        conf.fatal('Magnum cannot be setup with GCC < 4.8!')

    includes_check = ['/usr/local/include', '/usr/include', '/opt/local/include', '/sw/include']
    libs_check = ['/usr/lib', '/usr/local/lib', '/opt/local/lib', '/sw/lib', '/lib', '/usr/lib/x86_64-linux-gnu/', '/usr/lib64']
    bins_check = ['/usr/bin', '/usr/local/bin', '/opt/local/bin', '/sw/bin', '/bin']

    # Magnum depends on several libraries and we cannot make the assumption that
    # someone installed all of them in the same directory!
    # to-do: a better? solution would be to create different scripts for each dependency
    if conf.options.magnum_install_dir:
        includes_check = [conf.options.magnum_install_dir + '/include'] + includes_check
        libs_check = [conf.options.magnum_install_dir + '/lib'] + libs_check
        bins_check = [conf.options.magnum_install_dir + '/bin'] + bins_check

    required = kw.get('required', False)
    requested_components = kw.get('components', None)
    if requested_components == None:
        requested_components = []
    else:
        requested_components = requested_components.split()

    corrade_var = kw.get('corrade', 'CORRADE')

    # # Magnum requires Corrade
    # conf.check_corrade(components='Utility PluginManager', uselib_store='MAGNUM_CORRADE', required=True)
    if not conf.env['INCLUDES_%s' % corrade_var]:
        conf.fatal('Magnum requires Corrade! Cannot proceed!')
    if not conf.env['INCLUDES_%s_Utility' % corrade_var]:
        conf.fatal('Magnum requires Corrade Utility library! Cannot proceed!')
    if not conf.env['INCLUDES_%s_PluginManager' % corrade_var]:
        conf.fatal('Magnum requires Corrade PluginManager library! Cannot proceed!')

    # put the Corrade includes/libpaths/libs/bins to Magnum
    # magnum_includes = copy.deepcopy(conf.env['INCLUDES_MAGNUM_CORRADE'])
    # magnum_libpaths = copy.deepcopy(conf.env['LIBPATH_MAGNUM_CORRADE'])
    # magnum_libs = copy.deepcopy(conf.env['LIB_MAGNUM_CORRADE'])
    # magnum_bins = copy.deepcopy(conf.env['EXEC_MAGNUM_CORRADE'])
    magnum_includes = copy.deepcopy(conf.env['INCLUDES_%s' % corrade_var])
    magnum_libpaths = copy.deepcopy(conf.env['LIBPATH_%s' % corrade_var])
    magnum_libs = copy.deepcopy(conf.env['LIB_%s' % corrade_var])
    magnum_bins = copy.deepcopy(conf.env['EXEC_%s' % corrade_var])

    magnum_var = kw.get('uselib_store', 'MAGNUM')
    # to-do: enforce C++11/14

    magnum_possible_configs = ["BUILD_DEPRECATED", "BUILD_STATIC", "BUILD_MULTITHREADED", "TARGET_GLES", "TARGET_GLES2", "TARGET_GLES3", "TARGET_DESKTOP_GLES", "TARGET_WEBGL", "TARGET_HEADLESS"]
    magnum_config = []

    magnum_components = ['Audio', 'DebugTools', 'MeshTools', 'Primitives', 'SceneGraph', 'Shaders', 'Shapes', 'Text', 'TextureTools', 'GlfwApplication', 'GlutApplication', 'GlxApplication', 'Sdl2Application', 'XEglApplication', 'WindowlessCglApplication', 'WindowlessEglApplication', 'WindowlessGlxApplication', 'WindowlessIosApplication', 'WindowlessWglApplication', 'WindowlessWindowsEglApplicatio', 'CglContext', 'EglContext', 'GlxContext', 'WglContext', 'OpenGLTester', 'MagnumFont', 'MagnumFontConverter', 'ObjImporter', 'TgaImageConverter', 'TgaImporter', 'WavAudioImporter', 'distancefieldconverter', 'fontconverter', 'imageconverter', 'info', 'al-info']
    magnum_dependencies = {}
    for component in magnum_components:
        magnum_dependencies[component] = []
    magnum_dependencies['Shapes'] = ['SceneGraph']
    magnum_dependencies['Text'] = ['TextureTools']
    magnum_dependencies['DebugTools'] = ['MeshTools', 'Primitives', 'SceneGraph', 'Shaders', 'Shapes']
    # to-do: OpenGLTester deps should be defined after the configurations have been detected
    magnum_dependencies['MagnumFont'] = ['TgaImporter', 'Text', 'TextureTools']
    magnum_dependencies['MagnumFontConverter'] = ['TgaImageConverter', 'Text', 'TextureTools']
    magnum_dependencies['ObjImporter'] = ['MeshTools']
    magnum_dependencies['WavAudioImporter'] = ['Audio']

    magnum_component_type = {}
    for component in magnum_components:
        magnum_component_type[component] = ''
        pat_lib = re.compile('^(Audio|DebugTools|MeshTools|Primitives|SceneGraph|Shaders|Shapes|Text|TextureTools|AndroidApplication|GlfwApplication|GlutApplication|GlxApplication|Sdl2Application|XEglApplication|WindowlessCglApplication|WindowlessEglApplication|WindowlessGlxApplication|WindowlessIosApplication|WindowlessWglApplication|WindowlessWindowsEglApplication|CglContext|EglContext|GlxContext|WglContext|OpenGLTester)$')
        pat_plugin = re.compile('^(MagnumFont|MagnumFontConverter|ObjImporter|TgaImageConverter|TgaImporter|WavAudioImporter)$')
        pat_bin = re.compile('^(distancefieldconverter|fontconverter|imageconverter|info|al-info)$')
        if re.match(pat_lib, component):
            magnum_component_type[component] = 'lib'
        if re.match(pat_plugin, component):
            magnum_component_type[component] = 'plugin'
        if re.match(pat_bin, component):
            magnum_component_type[component] = 'bin'

    magnum_component_includes = {}
    magnum_component_libpaths = {}
    magnum_component_libs = {}
    magnum_component_bins = {}

    try:
        # to-do: support both debug and release builds
        conf.start_msg('Checking for Magnum includes')
        magnum_include_dir = get_directory('Magnum/Magnum.h', includes_check)
        magnum_includes = magnum_includes + [magnum_include_dir, magnum_include_dir + '/MagnumExternal/OpenGL']
        conf.end_msg(magnum_include_dir)

        conf.start_msg('Checking for Magnum lib')
        magnum_lib_path = get_directory('libMagnum.so', libs_check)
        magnum_libpaths = magnum_libpaths + [magnum_lib_path]
        magnum_libs = magnum_libs + ['Magnum']
        conf.end_msg(['Magnum'])

        conf.start_msg('Getting Magnum configuration')
        config_file = conf.find_file('Magnum/configure.h', includes_check)
        with open(config_file) as f:
            config_content = f.read()
        for config in magnum_possible_configs:
            index = find_in_string(config_content, '#define MAGNUM_' + config)
            if index > -1:
                magnum_config.append(config)
        conf.end_msg(magnum_config)

        # to-do: set plugin dir
        # to-do: make it work for other platforms; now only for desktop
        conf.start_msg('Magnum: Checking for OpenGL includes')
        opengl_include_dir = get_directory('GL/gl.h', includes_check)
        magnum_includes = magnum_includes + [opengl_include_dir]
        conf.end_msg(opengl_include_dir)

        conf.start_msg('Magnum: Checking for OpenGL lib')
        opengl_lib_dir = get_directory('libGL.so', libs_check)
        magnum_libpaths = magnum_libpaths + [opengl_lib_dir]
        magnum_libs = magnum_libs + ['GL']
        conf.end_msg(['GL'])

        conf.start_msg('Checking for Magnum components')
        # only check for components that can exist
        requested_components = list(set(requested_components).intersection(magnum_components))
        # add dependencies
        for lib in requested_components:
            requested_components = requested_components + magnum_dependencies[lib]
        # remove duplicates
        requested_components = list(set(requested_components))

        initial_magnum_include_dirs = copy.deepcopy(magnum_includes)
        initial_magnum_libpaths = copy.deepcopy(magnum_libpaths)
        initial_magnum_libs = copy.deepcopy(magnum_libs)
        initial_magnum_bins = copy.deepcopy(magnum_bins)

        for component in requested_components:
            # get general Magnum includes/libs/paths
            magnum_component_includes[component] = copy.deepcopy(initial_magnum_include_dirs)
            magnum_component_libpaths[component] = copy.deepcopy(initial_magnum_libpaths)
            magnum_component_libs[component] = copy.deepcopy(initial_magnum_libs)
            magnum_component_bins[component] = copy.deepcopy(initial_magnum_bins)

            # get component type
            component_type = magnum_component_type[component]
            if component_type == 'lib':
                pat_app = re.compile('.+Application')
                pat_context = re.compile('.+Context')

                component_file = component
                if component == 'MeshTools':
                    component_file = 'CompressIndices'
                if component == 'Primitives':
                    component_file = 'Cube'
                if component == 'TextureTools':
                    component_file = 'Atlas'

                lib_type = 'so'
                include_prefix = component

                # Applications
                if re.match(pat_app, component):
                    # to-do: all of them are static?
                    lib_type = 'a'
                    include_prefix = 'Platform'

                    if component == 'GlfwApplication':
                        # GlfwApplication requires GLFW3
                        # conf.start_msg('Magnum: Checking for GLFW3 includes')
                        glfw_inc = get_directory('GLFW/glfw3.h', includes_check)

                        magnum_includes = magnum_includes + [glfw_inc]
                        magnum_component_includes[component] = magnum_component_includes[component] + [glfw_inc]

                        # conf.start_msg('Magnum: Checking for GLFW3 lib')
                        libs_glfw = ['glfw', 'glfw3']
                        glfw_found = False
                        for lib_glfw in libs_glfw:
                            try:
                                lib_dir = get_directory('lib'+lib_glfw+'.so', libs_check)
                                glfw_found = True
                                magnum_libpaths = magnum_libpaths + [lib_dir]
                                magnum_libs.append(lib_glfw)

                                magnum_component_libpaths[component] = magnum_component_libpaths[component] + [lib_dir]
                                magnum_component_libs[component].append(lib_glfw)
                                break
                            except:
                                glfw_found = False
                        
                        if not glfw_found:
                            conf.fatal('Not found')
                    elif component == 'GlutApplication':
                        # GlutApplication requires GLUT
                        # conf.start_msg('Magnum: Checking for GLUT includes')
                        glut_inc = get_directory('GL/freeglut.h', includes_check)

                        magnum_includes = magnum_includes + [glut_inc]
                        magnum_component_includes[component] = magnum_component_includes[component] + [glut_inc]

                        # conf.start_msg('Magnum: Checking for GLFW3 lib')
                        libs_glut = ['glut', 'glut32']
                        glut_found = False
                        for lib_glut in libs_glut:
                            try:
                                lib_dir = get_directory('lib'+lib_glut+'.so', libs_check)
                                glut_found = True
                                magnum_libpaths = magnum_libpaths + [lib_dir]
                                magnum_libs.append(lib_glut)

                                magnum_component_libpaths[component] = magnum_component_libpaths[component] + [lib_dir]
                                magnum_component_libs[component].append(lib_glut)
                                break
                            except:
                                glut_found = False
                        
                        if not glut_found:
                            conf.fatal('Not found')
                    elif component == 'Sdl2Application':
                        # Sdl2Application requires SDL2
                        conf.check_cfg(path='sdl2-config', args='--cflags --libs', package='', uselib_store='MAGNUM_SDL')
                        magnum_includes = magnum_includes + conf.env['INCLUDES_MAGNUM_SDL']
                        magnum_component_includes[component] = magnum_component_includes[component] + conf.env['INCLUDES_MAGNUM_SDL']

                        magnum_libpaths = magnum_libpaths + conf.env['LIBPATH_MAGNUM_SDL']
                        magnum_libs = magnum_libs + conf.env['LIB_MAGNUM_SDL']

                        magnum_component_libpaths[component] = magnum_component_libpaths[component] + conf.env['LIBPATH_MAGNUM_SDL']
                        magnum_component_libs[component] = magnum_component_libs[component] + conf.env['LIB_MAGNUM_SDL']
                        # to-do: maybe copy flags?
                    elif component not in ['WindowlessCglApplication', 'WindowlessWglApplication']:
                        # to-do: support all other applications
                        msg = 'Component ' + component + ' is not yet supported by WAF'
                        Logs.pprint('RED', msg)
                        conf.fatal(msg)

                if re.match(pat_context, component) and component not in ['CglContext', 'WglContext']:
                    # to-do: support all other contexts
                    msg = 'Component ' + component + ' is not yet supported by WAF'
                    Logs.pprint('RED', msg)
                    conf.fatal(msg)

                include_dir = get_directory('Magnum/'+include_prefix+'/'+component_file+'.h', includes_check)
                magnum_includes = magnum_includes + [include_dir]
                lib = 'Magnum'+component
                lib_dir = get_directory('lib'+lib+'.'+lib_type, libs_check)
                magnum_libs.append(lib)
                magnum_libpaths = magnum_libpaths + [lib_dir]

                magnum_component_includes[component] = magnum_component_includes[component] + [include_dir]
                magnum_component_libpaths[component] = magnum_component_libpaths[component] + [lib_dir]
                magnum_component_libs[component].append(lib)

                # Audio lib required OpenAL
                if component == 'Audio':
                    # conf.start_msg('Magnum: Checking for OpenAL includes')
                    includes_audio = ['AL', 'OpenAL']
                    openal_found = False
                    for inc in includes_audio:
                        try:
                            # we need the full include dir
                            incl_audio = get_directory(inc+'/al.h', includes_check, True)
                            openal_found = True
                            magnum_includes = magnum_includes + [incl_audio]

                            magnum_component_includes[component] = magnum_component_includes[component] + [incl_audio]
                            break
                        except:
                            openal_found = False
                    
                    if not openal_found:
                        conf.fatal('Not found')

                    # conf.start_msg('Magnum: Checking for OpenAL lib')
                    libs_audio = ['OpenAL', 'al', 'openal', 'OpenAL32']
                    openal_found = False
                    for lib_audio in libs_audio:
                        try:
                            lib_dir = get_directory('lib'+lib_audio+'.so', libs_check)
                            openal_found = True
                            magnum_libpaths = magnum_libpaths + [lib_dir]
                            magnum_libs.append(lib_audio)

                            magnum_component_libpaths[component] = magnum_component_libpaths[component] + [lib_dir]
                            magnum_component_libs[component].append(lib_audio)
                            break
                        except:
                            openal_found = False
                    
                    if not openal_found:
                        conf.fatal('Not found')
            if component_type == 'plugin':
                pat_audio = re.compile('.+AudioImporter$')
                pat_importer = re.compile('.+Importer$')
                pat_font = re.compile('.+Font$')
                pat_img_conv = re.compile('.+ImageConverter$')
                pat_font_conv = re.compile('.+FontConverter$')

                lib_path_suffix = ''
                component_file = component

                if re.match(pat_audio, component):
                    lib_path_suffix = 'audioimporters'
                    component_file = component.replace("AudioImporter", "Importer")
                elif re.match(pat_importer, component):
                    lib_path_suffix = 'importers'
                elif re.match(pat_font, component):
                    lib_path_suffix = 'fonts'
                elif re.match(pat_img_conv, component):
                    lib_path_suffix = 'imageconverters'
                elif re.match(pat_font_conv, component):
                    lib_path_suffix = 'fontconverters'

                if lib_path_suffix != '':
                    lib_path_suffix = lib_path_suffix + '/'
                
                include_dir = get_directory('MagnumPlugins/'+component+'/'+component_file+'.h', includes_check)
                magnum_includes = magnum_includes + [include_dir]
                lib = component
                # we need the full lib_dir in order to be able to link to the plugins
                # or not? because they are loaded dynamically
                lib_dir = get_directory('magnum/'+lib_path_suffix+lib+'.so', libs_check, True)
                magnum_libs.append(lib)
                magnum_libpaths = magnum_libpaths + [lib_dir]

                magnum_component_includes[component] = magnum_component_includes[component] + [include_dir]
                magnum_component_libpaths[component] = magnum_component_libpaths[component] + [lib_dir]
                magnum_component_libs[component].append(lib)

            if component_type == 'bin':
                bin_name = 'magnum-'+component
                executable = conf.find_file(bin_name, bins_check)
                magnum_bins = magnum_bins + [executable]

                magnum_component_bins[component] = magnum_component_bins[component] + [executable]

        #remove duplicates
        magnum_includes = list(set(magnum_includes))
        magnum_libpaths = list(set(magnum_libpaths))
        conf.end_msg(magnum_libs + magnum_bins)

        # set environmental variables
        conf.env['INCLUDES_%s' % magnum_var] = magnum_includes
        conf.env['LIBPATH_%s' % magnum_var] = magnum_libpaths
        conf.env['LIB_%s' % magnum_var] = magnum_libs
        conf.env['EXEC_%s' % magnum_var] = magnum_bins

        # Plugin directories
        magnum_plugins_dir = magnum_lib_path + '/magnum'
        magnum_plugins_font_dir = magnum_plugins_dir + '/fonts'
        magnum_plugins_fontconverter_dir = magnum_plugins_dir + '/fontconverters'
        magnum_plugins_imageconverter_dir = magnum_plugins_dir + '/imageconverters'
        magnum_plugins_importer_dir = magnum_plugins_dir + '/importers'
        magnum_plugins_audioimporter_dir = magnum_plugins_dir + '/audioimporters'

        # conf.env['%s_PLUGINS_DIR' % magnum_var] = magnum_plugins_dir
        # conf.env['%s_PLUGINS_FONT_DIR' % magnum_var] = magnum_plugins_font_dir
        # conf.env['%s_PLUGINS_FONTCONVERTER_DIR' % magnum_var] = magnum_plugins_fontconverter_dir
        # conf.env['%s_PLUGINS_IMAGECONVERTER_DIR' % magnum_var] = magnum_plugins_imageconverter_dir
        # conf.env['%s_PLUGINS_IMPORTER_DIR' % magnum_var] = magnum_plugins_importer_dir
        # conf.env['%s_PLUGINS_AUDIOIMPORTER_DIR' % magnum_var] = magnum_plugins_audioimporter_dir

        # set C++ defines
        conf.env['DEFINES_%s' % magnum_var] = []
        conf.env['DEFINES_%s' % magnum_var].append('%s_PLUGINS_DIR="%s"' % (magnum_var, magnum_plugins_dir))
        conf.env['DEFINES_%s' % magnum_var].append('%s_PLUGINS_FONT_DIR="%s"' % (magnum_var, magnum_plugins_font_dir))
        conf.env['DEFINES_%s' % magnum_var].append('%s_PLUGINS_FONTCONVERTER_DIR="%s"' % (magnum_var, magnum_plugins_fontconverter_dir))
        conf.env['DEFINES_%s' % magnum_var].append('%s_PLUGINS_IMAGECONVERTER_DIR="%s"' % (magnum_var, magnum_plugins_imageconverter_dir))
        conf.env['DEFINES_%s' % magnum_var].append('%s_PLUGINS_IMPORTER_DIR="%s"' % (magnum_var, magnum_plugins_importer_dir))
        conf.env['DEFINES_%s' % magnum_var].append('%s_PLUGINS_AUDIOIMPORTER_DIR="%s"' % (magnum_var, magnum_plugins_audioimporter_dir))


        # set component libs
        for component in requested_components:
            for lib in magnum_dependencies[component]:
                magnum_component_includes[component] = magnum_component_includes[component] + magnum_component_includes[lib]
                magnum_component_libpaths[component] = magnum_component_libpaths[component] + magnum_component_libpaths[lib]
                magnum_component_libs[component] = magnum_component_libs[component] + magnum_component_libs[lib]
                magnum_component_bins[component] = magnum_component_bins[component] + magnum_component_bins[lib]

            conf.env['INCLUDES_%s_%s' % (magnum_var, component)] = list(set(magnum_component_includes[component]))
            conf.env['LIBPATH_%s_%s' % (magnum_var, component)] = list(set(magnum_component_libpaths[component]))
            conf.env['LIB_%s_%s' % (magnum_var, component)] = list(set(magnum_component_libs[component]))
            conf.env['EXEC_%s_%s' % (magnum_var, component)] = list(set(magnum_component_bins[component]))

            conf.env['DEFINES_%s_%s' % (magnum_var, component)] = copy.deepcopy(conf.env['DEFINES_%s' % magnum_var])
        # set C++ flags
        # conf.env['CXX_FLAGS_%s' % magnum_var] = copy.deepcopy(conf.env['CXX_FLAGS_MAGNUM_CORRADE'])
        conf.env['CXX_FLAGS_%s' % magnum_var] = copy.deepcopy(conf.env['CXX_FLAGS_%s' % corrade_var])
    except:
        if required:
            conf.fatal('Not found')
        conf.end_msg('Not found', 'RED')
        return
    return 1
