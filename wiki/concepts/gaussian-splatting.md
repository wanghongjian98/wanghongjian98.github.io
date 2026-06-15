---
title: "Gaussian Splatting"
type: concept
---

# Gaussian Splatting

## Summary

Gaussian Splatting 用一组可优化的 Gaussian primitives 表示场景或体数据，并通过 differentiable splatting / rendering 实现高效渲染和重建。最初它在 real-time novel view synthesis 中快速发展，现在已经扩展到 dynamic scenes、event cameras、X-ray/tomography 和 physics-aware reconstruction。

在本库中，Gaussian Splatting 是 [[Neural Field]] 和 explicit representation 之间的重要桥梁：它比纯 MLP 神经场更显式、更快，但如何加入物理 forward model、稀疏视角约束和连续时间运动仍是核心问题。

## Key Questions

- Gaussian 表示的是 surface、radiance field、density/attenuation field，还是 dynamic particles？
- 在 X-ray / tomography 中，Gaussian splatting 如何满足投影物理和 attenuation model？
- 3DGS 在 sparse-view、motion blur、event data 或 dynamic scenes 下如何避免漂移和伪结构？
- 显式 Gaussian primitives 与 implicit neural field 相比，优化稳定性、内存和泛化能力如何权衡？
- 如何把 deformation、time、material property 和 physical constraints 加入 Gaussian representation？

## Related Concepts

- [[Neural Field]]
- [[Implicit Neural Representation]]
- [[Tomography]]
- [[X-ray CT]]
- [[Event Camera]]
- [[Dynamic Imaging]]

## Reading Focus

- 区分 RGB novel view synthesis、dynamic 3DGS、event-guided 3DGS、radiative/X-ray 3DGS。
- 记录每篇论文的 primitive parameterization、rendering equation、regularization 和 data requirement。
- 特别关注 sparse-view CT 和 event-based deblurring 两条交叉线。

## Paper Mentions
- [[3D Gaussian Splatting for Real-Time Radiance Field Rendering]]
- [[Deformable 3D Gaussians for High-Fidelity Monocular Dynamic Scene Reconstruction]]
- [[DynMF: Neural Motion Factorization for Real-time Dynamic View Synthesis with 3D Gaussian Splatting]]
- [[GauFRe: Gaussian Deformation Fields for Real-time Dynamic Novel View Synthesis]]
- [[Real-time Photorealistic Dynamic Scene Representation and Rendering with 4D Gaussian Splatting]]
- [[SuGaR: Surface-Aligned Gaussian Splatting for Efficient 3D Mesh Reconstruction and High-Quality Mesh Rendering]]
- [[2D Gaussian Splatting for Geometrically Accurate Radiance Fields]]
- [[3D Gaussian Splatting as New Era: A Survey]]
- [[3D Geometry-Aware Deformable Gaussian Splatting for Dynamic View Synthesis]]
- [[4D Gaussian Splatting for Real-Time Dynamic Scene Rendering]]
- [[A Survey on 3D Gaussian Splatting]]
- [[Benchmarking Implicit Neural Representation and Geometric Rendering in Real-Time RGB-D SLAM]]
- [[CoGS: Controllable Gaussian Splatting]]
- [[Compact 3D Gaussian Splatting for Static and Dynamic Radiance Fields]]
- [[DDGS-CT: Direction-Disentangled Gaussian Splatting for Realistic Volume Rendering]]
- [[Depth-Regularized Optimization for 3D Gaussian Splatting in Few-Shot Images]]
- [[Dynamic 3D Gaussian Fields for Urban Areas]]
- [[Dynamic 3D Gaussians: Tracking by Persistent Dynamic View Synthesis]]
- [[E-3DGS: Gaussian Splatting with Exposure and Motion Events]]
- [[E2GS: Event Enhanced Gaussian Splatting]]
- [[EaDeblur-GS: Event assisted 3D Deblur Reconstruction with Gaussian Splatting]]
- [[EF-3DGS: Event-Aided Free-Trajectory 3D Gaussian Splatting]]
- [[Elite-EvGS: Learning Event-based 3D Gaussian Splatting by Distilling Event-to-Video Priors]]
- [[Event-3DGS: Event-based 3D Reconstruction Using 3D Gaussian Splatting]]
- [[Gaussian-Flow: 4D Reconstruction with Dynamic 3D Gaussian Particle]]
- [[Gaussian Splatting: 3D Reconstruction and Novel View Synthesis: A Review]]
- [[gsplat: An Open-Source Library for Gaussian Splatting]]
- [[IncEventGS: Pose-Free Gaussian Splatting from a Single Event Camera]]
- [[Learning 3D Gaussians for Extremely Sparse-View Cone-Beam CT Reconstruction]]
- [[LSE-NeRF: Learning Sensor Modeling Errors for Deblured Neural Radiance Fields with RGB-Event Stereo]]
- [[MoDGS: Dynamic Gaussian Splatting from Casually-captured Monocular Videos]]
- [[Neural Radiance Fields in Medical Imaging: Challenges and Next Steps]]
- [[PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics]]
- [[R$^2$-Gaussian: Rectifying Radiative Gaussian Splatting for Tomographic Reconstruction]]
- [[Radiative Gaussian Splatting for Efficient X-ray Novel View Synthesis]]
- [[Reconstructing Satellites in 3D from Amateur Telescope Images]]
- [[Reconstruction and Simulation of Elastic Objects with Spring-Mass 3D Gaussians]]
- [[SC-GS: Sparse-Controlled Gaussian Splatting for Editable Dynamic Scenes]]
- [[SpikeNVS: Enhancing Novel View Synthesis from Blurry Images via Spike Camera]]
- [[Unleashing the Potential of Multi-modal Foundation Models and Video Diffusion for 4D Dynamic Physical Scene Simulation]]
- [[3D Gaussian Splatting: Survey, Technologies, Challenges, and Opportunities]]
- [[3DGR-CT: Sparse-view CT reconstruction with a 3D Gaussian representation]]
- [[A Survey on Event-driven 3D Reconstruction: Development under Different Categories]]
- [[AE-NeRF: Augmenting Event-Based Neural Radiance Fields for Non-ideal Conditions and Larger Scene]]
- [[DeblurSplat: SfM-free 3D Gaussian Splatting with Event Camera for Robust Deblurring]]
- [[Discretized Gaussian Representation for Tomographic Reconstruction]]
- [[E-3DGS: Event-Based Novel View Rendering of Large-Scale Scenes Using 3D Gaussian Splatting]]
- [[X-Field: A Physically Grounded Representation for 3D X-ray Reconstruction]]
- [[X-LRM: X-ray Large Reconstruction Model for Extremely Sparse-View Computed Tomography Recovery in One Second]]
- [[X$^{2}$-Gaussian: 4D Radiative Gaussian Splatting for Continuous-time Tomographic Reconstruction]]
