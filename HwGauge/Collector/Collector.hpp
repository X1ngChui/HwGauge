#pragma once
#include <string>
#include <memory>

namespace hwgauge {
    using Registry = prometheus::Registry;
	class Collector {
    public:
        explicit Collector(std::shared_ptr<Registry> registry)
            : registry(std::move(registry)) {
        }

        virtual ~Collector() = default;
        
        virtual std::string name() = 0;
        virtual void collect() = 0;

        Collector(const Collector&) = delete;
        Collector& operator=(const Collector&) = delete;
    protected:
        std::shared_ptr<Registry> registry;
	};
}