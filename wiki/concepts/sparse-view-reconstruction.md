---
title: "Sparse-view Reconstruction"
type: concept
---

# Sparse-view Reconstruction

## Summary

Sparse-view Reconstruction 是在观测角度、投影数量或采样数据不足时恢复目标结构的逆问题。它在 CT、CBCT、X-ray tomography、NeRF/3D reconstruction 和 dynamic imaging 中都很常见，核心困难是问题高度欠定，容易出现 streak artifact、missing structure 和 hallucination。

本页关注如何用物理模型、稀疏先验、deep prior、diffusion prior、INR/neural field 或 Gaussian representation 在有限观测下稳定重建。

## Key Questions

- sparse-view 的稀疏性来自低剂量、快速采集、硬件限制，还是动态场景？
- 方法依赖 analytic reconstruction、iterative optimization、deep network、INR，还是 generative prior？
- 如何保证 data consistency，避免 learned prior 生成不存在的结构？
- sparse-view 与 limited-angle 是同一问题吗？各自的 artifact 和不可观测空间有什么不同？
- 评估是否只在 synthetic data 上成立，还是经过真实 scan / beamline / clinical 数据验证？

## Related Concepts

- [[Tomography]]
- [[X-ray CT]]
- [[Implicit Neural Representation]]
- [[Neural Field]]
- [[Diffusion Model]]
- [[Gaussian Splatting]]

## Reading Focus

- 记录 views/angles、dose、geometry、phantom/real data 和 baseline。
- 特别关注 projection-domain loss、image-domain prior 和 physical consistency 的组合。
- 对生成式方法，检查 uncertainty 和 hallucination 风险。

## Paper Mentions
- [[Super-Resolution and Sparse View CT Reconstruction]]
- [[Space-Time Tomographic Reconstruction of Deforming Objects]]
- [[SNAF: Sparse-view CBCT Reconstruction with Neural Attenuation Fields]]
- [[Geometry-Aware Attenuation Learning for Sparse-View CBCT Reconstruction]]
- [[Ultrasparse View X-ray Computed Tomography for 4D Imaging]]
- [[3D Gaussian Splatting as New Era: A Survey]]
- [[C^2RV: Cross-Regional and Cross-View Learning for Sparse-View CBCT Reconstruction]]
- [[Learning 3D Gaussians for Extremely Sparse-View Cone-Beam CT Reconstruction]]
- [[Unleashing the Potential of Multi-modal Foundation Models and Video Diffusion for 4D Dynamic Physical Scene Simulation]]
- [[3DGR-CT: Sparse-view CT reconstruction with a 3D Gaussian representation]]
- [[DeblurSplat: SfM-free 3D Gaussian Splatting with Event Camera for Robust Deblurring]]
- [[Dual-Domain deep prior guided sparse-view CT reconstruction with multi-scale fusion attention]]
- [[Physics-informed 4D X-ray image reconstruction from ultra-sparse spatiotemporal data]]
- [[TPG-INR: Target Prior-Guided Implicit 3D CT Reconstruction for Enhanced Sparse-view Imaging]]
- [[Dynamic EventNeRF: Reconstructing General Dynamic Scenes from Multi-view Event Cameras]]
