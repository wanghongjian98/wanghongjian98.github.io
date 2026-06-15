---
title: "Dynamic Imaging"
type: concept
---

# Dynamic Imaging

## Summary

Dynamic Imaging 泛指成像对象、相机、照明或观测过程随时间变化的任务。它覆盖高速视频、event sensing、time-resolved X-ray imaging、dynamic CT、动态 neural rendering 和 4D reconstruction。

这个概念比 [[4D Imaging]] 更宽：Dynamic Imaging 可以只恢复 2D video、motion field 或时间序列指标；4D Imaging 通常要求恢复随时间变化的 3D volume 或 scene representation。

## Key Questions

- 动态来自样品形变、流体流动、相机运动、曝光变化，还是成像系统本身？
- 采样率是否足以捕捉目标动力学，还是必须依赖 motion prior？
- 重建目标是 frame sequence、3D/4D volume、continuous trajectory，还是可解释的动态参数？
- 如何处理 temporal aliasing、motion blur、rolling shutter 和 sparse measurement？
- 动态重建是否需要物理模型，如流体、弹性、呼吸周期或投影几何？

## Related Concepts

- [[4D Imaging]]
- [[Event Camera]]
- [[Tomography]]
- [[Image Restoration]]
- [[Neural Field]]

## Reading Focus

- 按成像模态区分：event video、X-ray radioscopy、dynamic CT、neural dynamic scenes。
- 记录 temporal sampling、motion assumption、data term 和 evaluation protocol。
- 对高速实验，重点关注硬件限制和数据吞吐。

## Paper Mentions
- [[Ultrafast three-dimensional x-ray computed tomography]]
- [[Tomographic in vivo microscopy for the study of lung physiology at the alveolar level]]
- [[Simultaneous Reciprocal and Real Space X-Ray Imaging of Time-EvolvingSystems]]
- [[Dynamic Tomography Reconstruction by Projection-Domain Separable Modeling]]
- [[Sparse Synthesis for Hyperdimensional Ptychographic Tomography]]
- [[Dynamic Tomography Reconstruction via Low-Rank Modeling with a RED Spatial Prior]]
- [[Event-based vision sensor for fast and dense single-molecule localization microscopy]]
- [[Solving 3D Inverse Problems Using Pre-Trained 2D Diffusion Models]]
- [[Ultrasparse View X-ray Computed Tomography for 4D Imaging]]
- [[Dynamic X-ray speckle-tracking imaging with high-accuracy phase retrieval based on deep learning]]
- [[Freeze casting]]
- [[Implicit neural representation for fast 4D computed tomography of multiphase flow in porous media]]
- [[X$^{2}$-Gaussian: 4D Radiative Gaussian Splatting for Continuous-time Tomographic Reconstruction]]
