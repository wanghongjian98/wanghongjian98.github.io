---
title: "Neuromorphic Vision"
type: concept
---

# Neuromorphic Vision

## Summary

Neuromorphic Vision 借鉴生物视觉系统，用事件驱动、异步、低功耗和高时间分辨率的方式感知视觉信息。它包括 event cameras、spiking sensors、in-sensor computing、spiking neural networks 和面向低延迟控制的视觉处理。

在本库中，Neuromorphic Vision 是 [[Event Camera]] 的上位概念：Event Camera 是最常见的硬件入口，而 neuromorphic vision 还包含算法、芯片架构、采样理论和 sensor-compute co-design。

## Key Questions

- neuromorphic vision 的优势来自 sensor hardware、event representation，还是 downstream algorithm？
- 事件驱动处理是否真正降低能耗和延迟，还是只是改变了数据格式？
- spiking neural networks 与 conventional deep networks 在视觉任务中如何比较？
- sensor bias、noise、latency 和 asynchronous sampling 如何影响系统设计？
- neuromorphic sensing 能否进入 X-ray、microscopy、SPAD 或 scientific imaging？

## Related Concepts

- [[Event Camera]]
- [[Dynamic Imaging]]
- [[Image Restoration]]
- [[Deblurring]]

## Reading Focus

- 区分硬件论文、算法论文、benchmark/dataset 论文和系统应用论文。
- 记录每篇论文是否真的利用异步事件结构，而不只是把 events 转成 frames。
- 关注 low-power / low-latency claim 是否有实测指标。

## Paper Mentions
- [[A 128 × 128 Asynchronous Temporal Contrast Vision Sensor with 120 dB Dynamic Range and 15 μs Latency]]
- [[Event-Based Feature Extraction Using Adaptive Selection Thresholds]]
- [[Neuromorphic vision sensors: Principle, progress and perspectives]]
- [[Are High-Resolution Event Cameras Really Needed?]]
- [[Autofocus for Event Cameras]]
- [[Achieving nanoscale precision using neuromorphic localization microscopy]]
- [[Computational event-driven vision sensors for in-sensor spiking neural networks]]
- [[Deep Polarization Reconstruction With PDAVIS Events]]
- [[Event-based camera refractory period characterization and initial clock drift evaluation]]
- [[Event-based vision sensor for fast and dense single-molecule localization microscopy]]
- [[Neuromorphic Sampling of Sparse Signals]]
- [[On the Generation of a Synthetic Event-Based Vision Dataset for Navigation and Landing]]
- [[PDAVIS: Bio-inspired Polarization Event Camera]]
- [[Real-Time Multi-Task Facial Analytics With Event Cameras]]
- [[V2CE: Video to Continuous Events Simulator]]
- [[On non-von Neumann flexible neuromorphic vision sensors]]
- [[A Survey on Event-driven 3D Reconstruction: Development under Different Categories]]
- [[Integer-Valued Training and Spike-Driven Inference Spiking Neural Network for High-Performance and Energy-Efficient Object Detection]]
- [[Pixel Latency Measurements of Event Cameras]]
- [[[PDF] Deep Polarization Reconstruction with PDAVIS Events | Semantic Scholar]]
