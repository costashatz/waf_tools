#include <Corrade/Containers/Array.h>
#include <Corrade/Containers/ArrayView.h>
#include <Corrade/PluginManager/Manager.h>
#include <Corrade/Utility/Directory.h>

#include <Magnum/Trade/AbstractImporter.h>

int main()
{
    Corrade::PluginManager::Manager<Magnum::Trade::AbstractImporter> manager{MAGNUM_PLUGINS_IMPORTER_DIR};
    std::unique_ptr<Magnum::Trade::AbstractImporter> importer = manager.loadAndInstantiate("AssimpImporter");

    auto data = Corrade::Utility::Directory::read(Corrade::Utility::Directory::join(ASSIMPIMPORTER_RES_DIR, "scene.dae"));
    bool opened = importer->openData(data);
    if (opened)
        Corrade::Utility::Debug{} << "Yay!";

    return 0;
}