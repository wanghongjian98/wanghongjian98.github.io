---
title: "Diffusion Model"
type: concept
---

# Diffusion Model

## Summary

Diffusion Model 是一类通过逐步加噪和反向去噪学习数据分布的生成模型。在本知识库中，它主要作为 inverse problems 的强先验出现，用于 sparse-view reconstruction、image restoration、3D reconstruction 和 dynamic scene generation。

它的重要性不在于“生成漂亮图像”，而在于它能把大规模数据学到的统计结构注入欠定问题。但这也带来风险：生成先验可能 hallucinate，和物理测量不一致，或者在医学/X-ray 场景中产生不可接受的伪结构。

## Key Questions

- Diffusion prior 是作为 posterior sampler、regularizer、plug-and-play prior，还是 data generator 使用？
- 数据一致性如何保证？是在每步采样中投影回 measurement space，还是只在 loss 中弱约束？
- 对 CT、tomography、event imaging 等物理成像问题，生成先验是否会引入 hallucination？
- 2D diffusion prior 如何迁移到 3D、4D 或投影域？
- 如何评估 uncertainty，而不是只报告单个重建结果？

## Related Concepts

- [[Image Restoration]]
- [[Sparse-view Reconstruction]]
- [[Tomography]]
- [[Neural Field]]
- [[Dynamic Imaging]]

## Reading Focus

- 优先关注 diffusion prior 和物理 forward model 如何耦合。
- 记录每篇论文的 measurement operator、conditioning signal、sampling cost 和 failure cases。
- 对医学和 X-ray 论文，重点检查是否有数据一致性和定量评估。

## Paper Mentions
- [[CompoNeRF: Text-guided Multi-object Compositional NeRF with Editable 3D Scene Layout]]
- [[Geometry-Aware Attenuation Learning for Sparse-View CBCT Reconstruction]]
- [[Improving 3D Imaging with Pre-Trained Perpendicular 2D Diffusion Models]]
- [[Solving 3D Inverse Problems Using Pre-Trained 2D Diffusion Models]]
- [[3D Gaussian Splatting as New Era: A Survey]]
- [[C^2RV: Cross-Regional and Cross-View Learning for Sparse-View CBCT Reconstruction]]
- [[Disentangled Cross-modal Fusion for Event-Guided Image Super-resolution]]
- [[Gaussian Splatting: 3D Reconstruction and Novel View Synthesis: A Review]]
- [[Learning 3D Gaussians for Extremely Sparse-View Cone-Beam CT Reconstruction]]
- [[MoDGS: Dynamic Gaussian Splatting from Casually-captured Monocular Videos]]
- [[PhysDreamer: Physics-Based Interaction with 3D Objects via Video Generation]]
- [[Unleashing the Potential of Multi-modal Foundation Models and Video Diffusion for 4D Dynamic Physical Scene Simulation]]
- [[3D Gaussian Splatting: Survey, Technologies, Challenges, and Opportunities]]
- [[3DGR-CT: Sparse-view CT reconstruction with a 3D Gaussian representation]]
- [[Generalizable Structure-Aware INF: Biplanar-View CT Reconstruction via Disentangled Implicit Neural Field]]
- [[PhysTwin: Physics-Informed Reconstruction and Simulation of Deformable Objects from Videos]]
- [[X-LRM: X-ray Large Reconstruction Model for Extremely Sparse-View Computed Tomography Recovery in One Second]]
- [[CS5242 : Neural Networks and Deep Learning]]
