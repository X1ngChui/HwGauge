#include "Exposer.hpp"
#include "spdlog/spdlog.h"
#include <exception>
#include <format>

namespace hwgauge {
	void Exposer::run() {
		running.store(true, std::memory_order_release);
		exposer.RegisterCollectable(registry);

		while (running.load(std::memory_order_acquire)) {
			collect();
		}
	}

	void Exposer::stop() {
		running.store(false, std::memory_order_release);
	}

	void Exposer::collect() {
		for (auto& collector : collectors) {
			std::string name = collector->name();
			try {
				collector->collect();
				spdlog::trace("Retrieve metrics from {} successfully", name);
			}
			catch (const std::exception& e) {
				spdlog::error("Faild to collect metrics from {}: {}", name, e.what());
			}
		}
	}
}