#pragma once

#include "prometheus/exposer.h"
#include "prometheus/registry.h"
#include "Collector/Collector.hpp"
#include <vector>
#include <memory>
#include <utility>
#include <atomic>
#include <chrono>
#include <spdlog/spdlog.h>

namespace hwgauge {
	class Exposer {
	public:
		Exposer(std::string address, std::chrono::seconds interval) :
			exposer(std::move(address)), registry(std::make_shared<Registry>()), interval(interval) {}

		template<typename T, typename... Args>
		void inline add_collector(Args&&... args) {
			collectors.push_back(std::make_unique<T>(registry, std::forward<Args>(args)...));
		}

		void run();
		void stop();
	private:
		void collect();
	private:
		prometheus::Exposer exposer;
		std::shared_ptr<Registry> registry;

		std::atomic<bool> running = false;
		std::chrono::seconds interval;
		std::vector<std::unique_ptr<Collector>> collectors;
	};
}