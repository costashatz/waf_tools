#include "abstract_road.hpp"

#include <Corrade/PluginManager/PluginMetadata.h>
#include <Corrade/Utility/ConfigurationGroup.h>

using namespace Corrade;

int main(int argc, char** argv)
{
    /* Import static plugin using the same name as in Canary.cpp */
    CORRADE_PLUGIN_IMPORT(Highway)

    Utility::Arguments args;
    args.addArgument("plugin").setHelp("plugin", "animal plugin name").addOption("plugin-dir", ".").setHelp("plugin-dir", "plugin directory to use", "DIR").setGlobalHelp("Displays info about given road.").parse(argc, argv);

    /* Initialize plugin manager with given directory */
    PluginManager::Manager<AbstractRoad> manager{args.value("plugin-dir")};

    /* Try to load a plugin */
    if (!(manager.load(args.value("plugin")) & PluginManager::LoadState::Loaded)) {
        Utility::Error{} << "The requested plugin" << args.value("plugin") << "cannot be loaded.";
        return 2;
    }

    /* Instance of an animal */
    std::unique_ptr<AbstractRoad> road = manager.instantiate(args.value("plugin"));

    Utility::Debug{} << "Using plugin" << '\'' + road->metadata()->data().value("name") + '\''
                     << "...\n";

    Utility::Debug{} << "Name:     " << road->name();
    Utility::Debug{} << "Is highway? " << (road->isHighway() ? "yes" : "no");

    return 0;
}