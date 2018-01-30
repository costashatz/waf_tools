#include <Corrade/Interconnect/Emitter.h>
#include <Corrade/Interconnect/Receiver.h>
#include <Corrade/Utility/Debug.h>
#include <string>

using namespace Corrade;

class RemoteControl : public Interconnect::Emitter {
public:
    Signal triggered(const std::string& channel)
    {
        return emit(&RemoteControl::triggered, channel);
    }
};

class TVChannel : public Interconnect::Receiver {
public:
    virtual ~TVChannel() {}

    virtual void open(const std::string& channel) = 0;
};

class MegaChannel : public TVChannel {
public:
    void open(const std::string& channel)
    {
        // if not our channel, ignore
        if (channel != "Mega") {
            return;
        }

        Utility::Debug{} << "Launching MegaChannel";

        delete this;
    }
};

class UltraChannel : public TVChannel {
public:
    void open(const std::string& channel)
    {
        // if not our channel, ignore
        if (channel != "Ultra") {
            return;
        }

        Utility::Debug{} << "Launching UltraChannel";

        delete this;
    }
};

int main()
{
    RemoteControl rc;
    TVChannel *mega = new MegaChannel,
              *ultra = new UltraChannel;

    Interconnect::connect(rc, &RemoteControl::triggered, *mega, &TVChannel::open);
    Interconnect::connect(rc, &RemoteControl::triggered, *ultra, &TVChannel::open);

    Utility::Debug{} << "Successfully configured" << rc.signalConnectionCount()
                     << "channels.";

    rc.triggered("Mega");
    rc.triggered("Ultra");

    if (rc.signalConnectionCount())
        Utility::Fatal{1} << "Could not watch TV!" << rc.signalConnectionCount()
                          << "channels were not able to connect";

    Utility::Debug{} << "Nice TV shows!";
}