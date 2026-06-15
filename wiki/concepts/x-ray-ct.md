---
title: "X-ray CT"
type: concept
---

# X-ray CT

## Summary

X-ray CT 用 X-ray 投影从多个角度恢复物体内部的 attenuation / density 结构，是医学影像、材料科学、生命科学和 synchrotron imaging 的基础技术。它是 [[Tomography]] 的核心实例，但更强调 X-ray 物理、探测器、剂量、扫描几何和实际系统限制。

在本库中，X-ray CT 与 sparse-view reconstruction、dynamic CT、4D imaging、neural fields 和 Gaussian splatting 直接相连。很多近期论文都在尝试用 learned priors 或 continuous representation 减少投影数量、提升速度或处理动态样品。

## Key Questions

- CT 几何是 parallel-beam、fan-beam、cone-beam、laminography，还是 beamline-specific setup？
- 主要限制是 dose、scan speed、detector readout、sample motion、limited angle，还是 reconstruction artifact？
- learned reconstruction 是否遵守 X-ray projection physics？
- 对 dynamic / 4D CT，运动建模和 temporal sampling 如何影响可重建性？
- 如何在实验数据中验证真实结构，而不是只用 simulated phantom？

## Related Concepts

- [[Tomography]]
- [[Sparse-view Reconstruction]]
- [[Dynamic Imaging]]
- [[4D Imaging]]
- [[Implicit Neural Representation]]
- [[Gaussian Splatting]]

## Reading Focus

- 重点看 sparse-view CT、dynamic CT、CBCT、synchrotron CT 和 neural/3DGS CT。
- 记录投影数量、角度覆盖、dose/exposure、reconstruction baseline 和 data availability。
- 对医学或材料论文，关注定量指标和物理可解释性。

## Paper Mentions
- [[Principles of computerized tomographic imaging]]
- [[Dynamic X-ray computed tomography]]
- [[Region-of-Interest Tomography for Grating-Based X-Ray Differential Phase-Contrast Imaging]]
- [[Ultrafast three-dimensional x-ray computed tomography]]
- [[X-ray computed tomography using curvelet sparse regularization]]
- [[Laboratory based study of dynamical processes by 4D X-ray CT with sub-second temporal resolution]]
- [[Low-dose CT via convolutional neural network]]
- [[Tomographic in vivo microscopy for the study of lung physiology at the alveolar level]]
- [[Image reconstruction by domain-transform manifold learning]]
- [[Learned Primal-Dual Reconstruction]]
- [[TomoPhantom, a software package to generate 2D–4D analytical phantoms for CT image reconstruction algorithm benchmarks]]
- [[Comparison of three undersampling approaches in computed tomography reconstruction]]
- [[Convolutional Sparse Coding for Compressed Sensing CT Reconstruction]]
- [[Deep learning for tomographic image reconstruction]]
- [[Space-Time Tomographic Reconstruction of Deforming Objects]]
- [[Time-resolved 3D imaging of two-phase fluid flow inside a steel fuel injector using synchrotron X-ray tomography]]
- [[Beamline K11 DIAD: a new instrument for dual imaging and diffraction at Diamond Light Source]]
- [[Deep denoising for multi-dimensional synchrotron X-ray tomography without high-quality reference data]]
- [[Dynamic CT Reconstruction from Limited Views with Implicit Neural Representations and Parametric Motion Fields]]
- [[Exploring frontiers of 4D X-ray tomography]]
- [[IntraTomo: Self-supervised Learning-based Tomography via Sinogram Synthesis and Prediction]]
- [[Deep 3D reconstruction of synchrotron X-ray computed tomography for intact lungs]]
- [[Detecting lithium plating dynamics in a solid-state battery with operando X-ray computed tomography using machine learning]]
- [[From micro- to nano- and time-resolved x-ray computed tomography: Bio-based applications, synchrotron capabilities, and data-driven processing]]
- [[Learning to Distill Global Representation for Sparse-View CT]]
- [[Needs, Trends, and Advances in Scintillators for Radiographic Imaging and Tomography]]
- [[Neural rendering enables dynamic tomography]]
- [[3DGR-CT: Sparse-view CT reconstruction with a 3D Gaussian representation]]
- [[Distributed Stochastic Optimization of a Neural Representation Network for Time-Space Tomography Reconstruction]]
- [[End-to-End Deep Learning for Interior Tomography with Low-Dose X-ray CT]]
- [[Enhancing Dynamic CT Image Reconstruction with Neural Fields and Optical Flow]]
- [[GLIMPSE: Generalized Locality for Scalable and Robust CT]]
- [[Ring Artifacts Removal Based on Implicit Neural Representation of Sinogram Data]]
- [[Synchrotron radiation sparse-view CT artifact correction through deep learning neural networks]]
- [[X-ray computed laminography: A brief review of mechanisms, reconstruction, applications and perspectives]]
