#include "abstract_road.hpp"

namespace Corrade {
    class Road : public AbstractRoad {
    public:
        Road(PluginManager::AbstractManager& manager, const std::string& plugin) : AbstractRoad{manager, plugin} {}

        std::string name() const override { return "Small road"; }
        bool isHighway() const override { return false; }
    };
} // namespace Corrade


CORRADE_PLUGIN_REGISTER(Road, Corrade::Road, "costashatz.waf_tools.examples.corrade.AbstractRoad/1.0")