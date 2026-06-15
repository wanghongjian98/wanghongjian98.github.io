---
title: "4D Imaging"
type: concept
---

# 4D Imaging

## Summary

4D Imaging 指在三维空间结构之外显式恢复时间维度的成像问题，目标是得到随时间演化的体数据、形变场、相变过程或动态结构。它通常比单帧 3D reconstruction 更难，因为采集速度、剂量、投影角度、运动模糊和重建稳定性会同时受限。

在本库中，4D Imaging 主要连接两条线：一条是 synchrotron / X-ray CT 中的高速动态体成像，另一条是 neural representation / Gaussian splatting / physics-informed model 对连续时间场的建模。它是把 [[Dynamic Imaging]]、[[Tomography]]、[[X-ray CT]] 和 [[Neural Field]] 接起来的核心概念。

## Key Questions

- 如何在极少投影、低剂量或非完整角度覆盖下恢复连续时间 3D 结构？
- 运动应该作为显式 deformation field、低秩时空模型、还是隐式神经场来表示？
- 采集系统的 temporal resolution、spatial resolution 和 signal-to-noise ratio 如何共同限制 4D reconstruction？
- 哪些任务需要真实 4D volume，哪些只需要关键状态、motion surrogate 或动态参数？
- 如何验证 4D reconstruction 的物理一致性，而不是只看视觉质量？

## Related Concepts

- [[Dynamic Imaging]]
- [[Tomography]]
- [[X-ray CT]]
- [[Neural Field]]
- [[Gaussian Splatting]]

## Reading Focus

- 优先读 sparse-view、ultrafast tomography、continuous-time reconstruction 和 motion-aware reconstruction 的论文。
- 对每篇论文记录 acquisition model、motion model、temporal prior、evaluation data 和 failure mode。
- 特别关注是否把时间作为离散帧处理，还是作为连续变量处理。

## Paper Mentions
- [[Space-Time Tomographic Reconstruction of Deforming Objects]]
- [[Smart lattice light-sheet microscopy for imaging rare and complex cellular events]]
- [[Ultrasparse View X-ray Computed Tomography for 4D Imaging]]
- [[Optimising 4D imaging of fast-oscillating structures using X-ray microtomography with retrospective gating]]
- [[The human middle ear in motion: 3D visualization and quantification using dynamic synchrotron-based X-ray imaging]]
- [[Physics-informed 4D X-ray image reconstruction from ultra-sparse spatiotemporal data]]
- [[X$^{2}$-Gaussian: 4D Radiative Gaussian Splatting for Continuous-time Tomographic Reconstruction]]
- [[A large-scale coherent 4D imaging sensor]]
