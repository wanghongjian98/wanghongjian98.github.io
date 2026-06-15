---
title: "Implicit Neural Representation"
type: concept
---

# Implicit Neural Representation

## Summary

Implicit Neural Representation (INR) 用神经网络把连续坐标映射到信号值，例如 density、attenuation、radiance、occupancy、deformation 或 intensity。它适合表示连续空间/时间信号，因此常用于 sparse-view CT、dynamic reconstruction、NeRF、medical imaging 和 scientific imaging。

INR 的价值在于连续性、可微性和 compact representation；风险在于优化慢、先验难解释、可能过平滑或 hallucinate。它和 [[Neural Field]] 基本同源，但本页更强调坐标网络作为通用表示形式。

## Key Questions

- 网络输入是 2D/3D/4D coordinates、view direction、time、projection angle，还是 latent code？
- INR 是直接表示对象，还是表示 correction、residual、motion field 或 prior？
- positional encoding、hash encoding、multi-resolution grid 对高频细节和稳定性有什么影响？
- 如何把物理 forward model 嵌入训练，而不是只拟合图像域？
- sparse-view / limited-angle 下 INR 的 implicit bias 是帮助还是风险？

## Related Concepts

- [[Neural Field]]
- [[Tomography]]
- [[Sparse-view Reconstruction]]
- [[Gaussian Splatting]]
- [[Dynamic Imaging]]

## Reading Focus

- 关注 coordinate representation、encoding、regularization 和 data consistency。
- 对 CT/CBCT 论文，记录 forward projector、projection loss 和几何假设。
- 对 dynamic tasks，记录 time/deformation 如何建模。

## Paper Mentions
- [[CoIL: Coordinate-based Internal Learning for Imaging Inverse Problems]]
- [[Dynamic CT Reconstruction from Limited Views with Implicit Neural Representations and Parametric Motion Fields]]
- [[NAF: Neural Attenuation Fields for Sparse-View CBCT Reconstruction]]
- [[Neural Fields in Visual Computing and Beyond]]
- [[Deep 3D reconstruction of synchrotron X-ray computed tomography for intact lungs]]
- [[Dynamic Tomography Reconstruction via Low-Rank Modeling with a RED Spatial Prior]]
- [[Generalizing Event-Based Motion Deblurring in Real-World Scenarios]]
- [[INeAT: Iterative Neural Adaptive Tomography]]
- [[Learning Spatial-Temporal Implicit Neural Representations for Event-Guided Video Super-Resolution]]
- [[ONIX: An X-ray deep-learning tool for 3D reconstructions from sparse views]]
- [[Benchmarking Implicit Neural Representation and Geometric Rendering in Real-Time RGB-D SLAM]]
- [[C^2RV: Cross-Regional and Cross-View Learning for Sparse-View CBCT Reconstruction]]
- [[Disentangled Cross-modal Fusion for Event-Guided Image Super-resolution]]
- [[Event Camera Demosaicing via Swin Transformer and Pixel-focus Loss]]
- [[Gaussian-Flow: 4D Reconstruction with Dynamic 3D Gaussian Particle]]
- [[Gaussian Splatting: 3D Reconstruction and Novel View Synthesis: A Review]]
- [[HR-INR: Continuous Space-Time Video Super-Resolution via Event Camera]]
- [[Imaging Interiors: An Implicit Solution to Electromagnetic Inverse Scattering Problems]]
- [[Learning 3D Gaussians for Extremely Sparse-View Cone-Beam CT Reconstruction]]
- [[Revisit Event Generation Model: Self-Supervised Learning of Event-to-Video Reconstruction with Implicit Neural Representations]]
- [[3DGR-CT: Sparse-view CT reconstruction with a 3D Gaussian representation]]
- [[DE-NAF: decoupled neural attenuation fields for sparse-view CBCT reconstruction]]
- [[Distributed Stochastic Optimization of a Neural Representation Network for Time-Space Tomography Reconstruction]]
- [[EvSTVSR: Event Guided Space-Time Video Super-Resolution]]
- [[Implicit neural representation for fast 4D computed tomography of multiphase flow in porous media]]
- [[Ring Artifacts Removal Based on Implicit Neural Representation of Sinogram Data]]
- [[Spatiotemporal-Aware Neural Fields for Dynamic CT Reconstruction]]
- [[Target Prior-enriched Implicit 3D CT Reconstruction with Adaptive Ray Sampling]]
