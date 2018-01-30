#include "abstract_road.hpp"

namespace Corrade {
    class Highway : public AbstractRoad {
    public:
        Highway(PluginManager::AbstractManager& manager, const std::string& plugin) : AbstractRoad{manager, plugin} {}

        std::string name() const override { return "Highway"; }
        bool isHighway() const override { return true; }
    };
} // namespace Corrade


CORRADE_PLUGIN_REGISTER(Highway, Corrade::Highway, "costashatz.waf_tools.examples.corrade.AbstractRoad/1.0")