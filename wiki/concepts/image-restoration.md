---
title: "Image Restoration"
type: concept
---

# Image Restoration

## Summary

Image Restoration 是从退化观测中恢复更高质量、更接近真实信号的图像或视频，包括 denoising、deblurring、super-resolution、low-light enhancement、interpolation 和 artifact removal。它是 inverse problems 的通用层，常作为 tomography、event camera、dynamic imaging 和 neural rendering 的前处理或联合优化模块。

在这个知识库里，Image Restoration 的关键不是单纯追求视觉效果，而是理解退化模型、数据一致性和下游任务影响：恢复结果是否有助于重建、测量或科学解释。

## Key Questions

- 退化模型是已知物理模型、经验噪声模型，还是完全 learned degradation？
- 恢复目标是 human-perceptual quality，还是 measurement fidelity / reconstruction accuracy？
- restoration 是否会引入 hallucination，特别是在医学和 X-ray 数据中？
- event stream、diffusion prior、neural field 或 Gaussian representation 能如何作为 restoration prior？
- 如何评估 restoration 对下游 tomography、3D reconstruction 或 segmentation 的影响？

## Related Concepts

- [[Deblurring]]
- [[Diffusion Model]]
- [[Event Camera]]
- [[Tomography]]
- [[Sparse-view Reconstruction]]

## Reading Focus

- 把论文按 degradation type 分类：noise、blur、low-light、missing views、compression/artifacts。
- 记录每篇论文的 forward model、loss、prior 和 evaluation metric。
- 对 scientific imaging，优先看 data fidelity 和 quantitative validation。

## Paper Mentions
- [[Learning Fast Approximations of Sparse Coding]]
- [[X-ray computed tomography using curvelet sparse regularization]]
- [[Low-dose CT via convolutional neural network]]
- [[Learned Primal-Dual Reconstruction]]
- [[Real-Time Intensity-Image Reconstruction for Event Cameras Using Manifold Regularisation]]
- [[Bringing Alive Blurred Moments]]
- [[Comparison of three undersampling approaches in computed tomography reconstruction]]
- [[Deep learning for tomographic image reconstruction]]
- [[Deep denoising for multi-dimensional synchrotron X-ray tomography without high-quality reference data]]
- [[Deblur-NeRF: Neural Radiance Fields from Blurry Images]]
- [[Event-Based Fusion for Motion Deblurring with Cross-modal Attention]]
- [[Plug-and-Play Algorithms for Video Snapshot Compressive Imaging]]
- [[Deep 3D reconstruction of synchrotron X-ray computed tomography for intact lungs]]
- [[E2NeRF: Event Enhanced Neural Radiance Fields from Blurry Images]]
- [[Ev-NeRF: Event Based Neural Radiance Field]]
- [[Learning INR for Event-guided Rolling Shutter Frame Correction, Deblur, and Interpolation]]
- [[Learning to Distill Global Representation for Sparse-View CT]]
- [[Non-Coaxial Event-guided Motion Deblurring with Spatial Alignment]]
- [[Deep Learning for Event-based Vision: A Comprehensive Survey and Benchmarks]]
- [[Disentangled Cross-modal Fusion for Event-Guided Image Super-resolution]]
- [[Event Camera Demosaicing via Swin Transformer and Pixel-focus Loss]]
- [[Structure-Aware Sparse-View X-Ray 3D Reconstruction]]
- [[Towards Robust Event-guided Low-Light Image Enhancement: A Large-Scale Real-World Event-Image Dataset and Novel Approach]]
- [[Deep learning-based spatio-temporal fusion for high-fidelity ultra-high-speed X-ray radiography]]
