---
title: "Neural Field"
type: concept
---

# Neural Field

## Summary

Neural Field 是用神经网络表示连续场的总称，包括 radiance field、density field、attenuation field、signed distance field、motion field 和 dynamic field。它把离散图像或体素重建转化为连续函数拟合，因此在 NeRF、medical imaging、tomography、dynamic reconstruction 和 inverse problems 中都很重要。

和 [[Implicit Neural Representation]] 相比，本页更强调“场”的物理或几何含义：网络不是只输出像素，而是在某个空间/时间域中表示可查询、可渲染、可微分的连续对象。

## Key Questions

- neural field 表示的是 radiance、attenuation、density、geometry、motion，还是多物理量耦合场？
- 训练信号来自 images、projections、events、depth，还是 simulation/physics constraints？
- 连续表示如何处理 high-frequency detail、sharp boundary 和 discontinuity？
- neural field 与 Gaussian splatting、voxel/grid、mesh 等显式表示如何取舍？
- 在 scientific imaging 中，neural field 的 uncertainty 和 physical validity 如何评估？

## Related Concepts

- [[Implicit Neural Representation]]
- [[Gaussian Splatting]]
- [[Tomography]]
- [[Dynamic Imaging]]
- [[4D Imaging]]

## Reading Focus

- 先区分 visual NeRF、medical neural field、tomographic neural field 和 dynamic neural field。
- 记录每篇论文的 field type、coordinate system、rendering/projection model 和 regularization。
- 重点关注 sparse data 下的 inductive bias。

## Paper Mentions
- [[Neural Fields in Visual Computing and Beyond]]
- [[Deformable Neural Radiance Fields using RGB and Event Cameras]]
- [[GauFRe: Gaussian Deformation Fields for Real-time Dynamic Novel View Synthesis]]
- [[ONIX: An X-ray deep-learning tool for 3D reconstructions from sparse views]]
- [[PAC-NeRF: Physics Augmented Continuum Neural Radiance Fields for Geometry-Agnostic System Identification]]
- [[Robust e-NeRF: NeRF from Sparse & Noisy Events under Non-Uniform Motion]]
- [[SuGaR: Surface-Aligned Gaussian Splatting for Efficient 3D Mesh Reconstruction and High-Quality Mesh Rendering]]
- [[3D Gaussian Splatting as New Era: A Survey]]
- [[Compact 3D Gaussian Splatting for Static and Dynamic Radiance Fields]]
- [[Dynamic 3D Gaussian Fields for Urban Areas]]
- [[Gaussian-Flow: 4D Reconstruction with Dynamic 3D Gaussian Particle]]
- [[Gaussian Splatting: 3D Reconstruction and Novel View Synthesis: A Review]]
- [[Hi-Map: Hierarchical Factorized Radiance Field for High-Fidelity Monocular Dense Mapping]]
- [[HR-INR: Continuous Space-Time Video Super-Resolution via Event Camera]]
- [[LSE-NeRF: Learning Sensor Modeling Errors for Deblured Neural Radiance Fields with RGB-Event Stereo]]
- [[PhysDreamer: Physics-Based Interaction with 3D Objects via Video Generation]]
- [[PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics]]
- [[Reconstructing Knee CT Volumes from Biplanar X-Rays Via Self-Supervised Neural Field]]
- [[SpikeNVS: Enhancing Novel View Synthesis from Blurry Images via Spike Camera]]
- [[3D Gaussian Splatting: Survey, Technologies, Challenges, and Opportunities]]
- [[Enhancing Dynamic CT Image Reconstruction with Neural Fields and Optical Flow]]
- [[Generalizable Structure-Aware INF: Biplanar-View CT Reconstruction via Disentangled Implicit Neural Field]]
- [[Neural Inverse Rendering from Propagating Light]]
- [[Neuromorphic computing at scale]]
- [[Ring Artifacts Removal Based on Implicit Neural Representation of Sinogram Data]]
- [[Spatiotemporal-Aware Neural Fields for Dynamic CT Reconstruction]]
