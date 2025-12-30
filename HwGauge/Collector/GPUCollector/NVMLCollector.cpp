#include "NVMLCollector.hpp"
#include <nvml.h>
#include <format>
#include <array>

namespace hwgauge {
	NVMLCollector::NVMLCollector(std::shared_ptr<Registry> registry)
		: GPUCollector<NVMLCollector>(std::move(registry))
	{
	}

	NVMLCollector::~NVMLCollector() {
		nvmlReturn_t status = nvmlShutdown();

		if (status != NVML_SUCCESS) {
			throw std::runtime_error(std::format("NVML shutdown failed: {}", nvmlErrorString(status)));
		}
	}

	std::vector<GPULabel> NVMLCollector::labels_impl() {
		nvmlReturn_t status;

		status = nvmlInit();
		if (status != NVML_SUCCESS) {
			throw std::runtime_error(std::format("NVML initialization failed: {}", nvmlErrorString(status)));
		}

		unsigned int devicesCount = 0;
		status = nvmlDeviceGetCount(std::addressof(devicesCount));

		if (status != NVML_SUCCESS) {
			throw std::runtime_error(std::format("NVML get devices count failed: {}", nvmlErrorString(status)));
		}

		std::vector<GPULabel> labels;
		for (std::size_t index = 0; index < devicesCount; index++) {
			nvmlDevice_t handle;
			status = nvmlDeviceGetHandleByIndex(index, std::addressof(handle));
			if (status != NVML_SUCCESS) {
				throw std::runtime_error(std::format("NVML get devices handle failed: {}", nvmlErrorString(status)));
			}

			std::array<char, NVML_DEVICE_NAME_BUFFER_SIZE> name = { 0 };
			status = nvmlDeviceGetName(handle, name.data(), name.size() - 1);
			if (status != NVML_SUCCESS) {
				throw std::runtime_error(std::format("NVML get devices name failed: {}", nvmlErrorString(status)));
			}

			GPULabel label = {
				.index = index,
				.name = std::string(name.data())
			};

			labels.emplace_back(std::move(label));
		}

		return labels;
	}

	std::vector<GPUMetrics> NVMLCollector::sample_impl() {
		nvmlReturn_t status;

		unsigned int devicesCount = 0;
		status = nvmlDeviceGetCount(std::addressof(devicesCount));
		if (status != NVML_SUCCESS) {
			throw std::runtime_error(std::format("NVML get devices count failed: {}", nvmlErrorString(status)));
		}

		std::vector<GPUMetrics> metrics;
		for (std::size_t index = 0; index < devicesCount; index++) {
			nvmlDevice_t handle;
			status = nvmlDeviceGetHandleByIndex(index, std::addressof(handle));
			if (status != NVML_SUCCESS) {
				throw std::runtime_error(std::format("NVML get devices handle failed: {}", nvmlErrorString(status)));
			}

			// GPU / Memory Utilization
			nvmlUtilization_t utilization;
			status = nvmlDeviceGetUtilizationRates(handle, std::addressof(utilization));
			if (status != NVML_SUCCESS) {
				throw std::runtime_error(std::format("NVML get utilizations rates failed: {}", nvmlErrorString(status)));
			}
			double gpuUtilization = utilization.gpu;
			double memoryUtilization = utilization.memory;

			// GPU Frequency
			unsigned int smClock;
			status = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_SM, std::addressof(smClock));
			if (status != NVML_SUCCESS) {
				throw std::runtime_error(std::format("NVML get SM clock info failed: {}", nvmlErrorString(status)));
			}
			double gpuFrequency = smClock;

			// Memory Frequency
			unsigned int memClock;
			status = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_MEM, std::addressof(memClock));
			if (status != NVML_SUCCESS) {
				throw std::runtime_error(std::format("NVML get memory clock info failed: {}", nvmlErrorString(status)));
			}
			double memFrequency = memClock;

			// Power Usage
			unsigned int power;
			status = nvmlDeviceGetPowerUsage(handle, std::addressof(power));
			if (status != NVML_SUCCESS) {
				throw std::runtime_error(std::format("NVML get power usage failed: {}", nvmlErrorString(status)));
			}
			double power_usage = power / 1e3;  // mW -> W

			metrics.emplace_back(GPUMetrics{
					.gpuUtilization = gpuUtilization,
					.memoryUtilization = memoryUtilization,
					.gpuFrequency = gpuFrequency,
					.memoryFrequency = memFrequency,
					.powerUsage = power_usage
				});
		}

		return metrics;
	}
}