#pragma once

#include "GPUCollector.hpp"
#include <string>
#include <vector>

namespace hwgauge {
	class NVMLCollector : public GPUCollector<NVMLCollector> {
	public:
		explicit NVMLCollector(std::shared_ptr<Registry> registry);
		~NVMLCollector();

		std::string name_impl() { return "NVML Collector"; }
		std::vector<GPULabel> labels_impl();
		std::vector<GPUMetrics> sample_impl();
	};
}