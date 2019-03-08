#include <Corrade/PluginManager/AbstractPlugin.h>
#include <Corrade/PluginManager/Manager.h>
#include <Corrade/Utility/Arguments.h>
#include <Corrade/Utility/Debug.h>

namespace Corrade {
    class AbstractRoad : public PluginManager::AbstractPlugin {
    public:
        AbstractRoad(PluginManager::AbstractManager& manager, const std::string& plugin) : AbstractPlugin{manager, plugin} {}

        virtual std::string name() const = 0;
        virtual bool isHighway() const = 0;

        static std::string pluginInterface()
        {
            return "costashatz.waf_tools.examples.corrade.AbstractRoad/1.0";
        }
    };
} // namespace Corrade