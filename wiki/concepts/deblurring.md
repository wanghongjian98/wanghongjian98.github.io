---
title: "Deblurring"
type: concept
---

# Deblurring

## Summary

Deblurring 是从运动模糊、离焦、低照度曝光或系统点扩散造成的退化图像中恢复清晰结构的逆问题。它在本库中不是孤立的图像增强任务，而是和 [[Event Camera]]、[[Image Restoration]]、[[Dynamic Imaging]]、[[Neural Field]] 以及 [[Gaussian Splatting]] 紧密相连。

对 event-based imaging 来说，Deblurring 的核心价值是利用事件流提供的高时间分辨率来补偿传统帧相机的长曝光模糊。对 neural rendering / 3DGS 来说，Deblurring 则影响相机位姿、几何重建和 novel view synthesis 的可靠性。

## Key Questions

- 模糊来自 camera motion、object motion、defocus、rolling shutter，还是传感器响应？
- 事件流、光流、深度、相机轨迹和神经表示分别能提供哪些约束？
- Deblurring 方法恢复的是 sharp frame、latent video、3D scene，还是可渲染的动态表示？
- 如何区分视觉锐化和真实几何/运动恢复？
- 在低光、高速运动、非线性曝光和真实噪声下，哪些先验最稳健？

## Related Concepts

- [[Event Camera]]
- [[Image Restoration]]
- [[Dynamic Imaging]]
- [[Gaussian Splatting]]
- [[Neural Field]]

## Reading Focus

- 先看 event-guided deblurring，再看 NeRF/3DGS deblurring。
- 记录每篇论文是否使用 events、frames、optical flow、depth、pose 或 learned prior。
- 特别关注 real-world generalization 和 blur formation model 是否可信。

## Paper Mentions
- [[Local computed tomography via iterative deblurring]]
- [[Learning Fast Approximations of Sparse Coding]]
- [[Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural Network]]
- [[Learning to Extract a Video Sequence from a Single Motion-Blurred Image]]
- [[Super SloMo: High Quality Estimation of Multiple Intermediate Frames for Video Interpolation]]
- [[TomoPhantom, a software package to generate 2D–4D analytical phantoms for CT image reconstruction algorithm benchmarks]]
- [[Bringing a Blurry Frame Alive at High Frame-Rate With an Event Camera]]
- [[Bringing Alive Blurred Moments]]
- [[On the use of deep learning for computational imaging]]
- [[Unsupervised Event-Based Learning of Optical Flow, Depth, and Egomotion]]
- [[Unsupervised Event-based Optical Flow using Motion Compensation]]
- [[Deep learning for tomographic image reconstruction]]
- [[Event Enhanced High-Quality Image Recovery]]
- [[Learning Event-Driven Video Deblurring and Interpolation]]
- [[Bringing Events Into Video Deblurring With Non-Consecutively Blurry Frames]]
- [[DSEC: A Stereo Event Camera Dataset for Driving Scenarios]]
- [[EvIntSR-Net: Event Guided Multiple Latent Frames Reconstruction and Super-Resolution]]
- [[Fine-Grained Video Deblurring with Event Camera]]
- [[Motion Deblurring With Real Events]]
- [[Time Lens: Event-based Video Frame Interpolation]]
- [[v2e: From Video Frames to Realistic DVS Events]]
- [[Deblur-NeRF: Neural Radiance Fields from Blurry Images]]
- [[Deep Image Deblurring: A Survey]]
- [[Event-Based Fusion for Motion Deblurring with Cross-modal Attention]]
- [[Event-based vision: a survey]]
- [[Event-guided Deblurring of Unknown Exposure Time Videos]]
- [[Self-Supervised Intensity-Event Stereo Matching]]
- [[SNAF: Sparse-view CBCT Reconstruction with Neural Attenuation Fields]]
- [[Time Lens++: Event-based Frame Interpolation with Parametric Non-linear Flow and Multi-scale Fusion]]
- [[TimeReplayer: Unlocking the Potential of Event Cameras for Video Interpolation]]
- [[Towards Interpretable Video Super-Resolution via Alternating Optimization]]
- [[Unifying Motion Deblurring and Frame Interpolation with Events]]
- [[Coherent Event Guided Low-Light Video Enhancement]]
- [[Deblurring Low-Light Images with Events]]
- [[Deformable Neural Radiance Fields using RGB and Event Cameras]]
- [[E-VFIA : Event-Based Video Frame Interpolation with Attention]]
- [[E2NeRF: Event Enhanced Neural Radiance Fields from Blurry Images]]
- [[Event-Based Image Deblurring with Dynamic Motion Awareness]]
- [[Event-based Video Frame Interpolation with Cross-Modal Asymmetric Bidirectional Motion Fields]]
- [[EventNeRF: neural radiance fields from a single colour event camera]]
- [[EventNeRF: Neural Radiance Fields from a Single Colour Event Camera]]
- [[Feature-enhanced X-ray imaging using fused neural network strategy with designable metasurface]]
- [[Generalizing Event-Based Motion Deblurring in Real-World Scenarios]]
- [[IDO-VFI: Identifying Dynamics via Optical Flow Guidance for Video Frame Interpolation with Events]]
- [[Learning INR for Event-guided Rolling Shutter Frame Correction, Deblur, and Interpolation]]
- [[Learning Spatial-Temporal Implicit Neural Representations for Event-Guided Video Super-Resolution]]
- [[Learning to Super-Resolve Blurry Images with Events]]
- [[Non-Coaxial Event-guided Motion Deblurring with Spatial Alignment]]
- [[Revisiting Event-based Video Frame Interpolation]]
- [[Revisiting Event-Based Video Frame Interpolation]]
- [[Self-Supervised Blind Motion Deblurring With Deep Expectation Maximization]]
- [[Self-supervised Learning of Event-guided Video Frame Interpolation for Rolling Shutter Frames]]
- [[SuperFast: 200× Video Frame Interpolation via Event Camera]]
- [[AgriNeRF: Neural Radiance Fields for Agriculture in Challenging Lighting Conditions]]
- [[An Asynchronous Linear Filter Architecture for Hybrid Event-Frame Cameras]]
- [[BeNeRF: Neural Radiance Fields from a Single Blurry Image and Event Stream]]
- [[Deblur e-NeRF: NeRF from Motion-Blurred Events under High-speed or Low-light Conditions]]
- [[Deblurring Neural Radiance Fields with Event-driven Bundle Adjustment]]
- [[Deep Learning for Event-based Vision: A Comprehensive Survey and Benchmarks]]
- [[Disentangled Cross-modal Fusion for Event-Guided Image Super-resolution]]
- [[Dynamic Gaussian Marbles for Novel View Synthesis of Casual Monocular Videos]]
- [[E2GS: Event Enhanced Gaussian Splatting]]
- [[E$^3$NeRF: Efficient Event-Enhanced Neural Radiance Fields from Blurry Images]]
- [[EaDeblur-GS: Event assisted 3D Deblur Reconstruction with Gaussian Splatting]]
- [[EF-3DGS: Event-Aided Free-Trajectory 3D Gaussian Splatting]]
- [[Event-3DGS: Event-based 3D Reconstruction Using 3D Gaussian Splatting]]
- [[Event Camera Demosaicing via Swin Transformer and Pixel-focus Loss]]
- [[EVS-Assisted Joint Deblurring, Rolling-Shutter Correction and Video Frame Interpolation Through Sensor Inverse Modeling]]
- [[Latency Correction for Event-Guided Deblurring and Frame Interpolation]]
- [[LSE-NeRF: Learning Sensor Modeling Errors for Deblured Neural Radiance Fields with RGB-Event Stereo]]
- [[Mitigating Motion Blur in Neural Radiance Fields with Events and Frames]]
- [[SC-GS: Sparse-Controlled Gaussian Splatting for Editable Dynamic Scenes]]
- [[SpikeNVS: Enhancing Novel View Synthesis from Blurry Images via Spike Camera]]
- [[SpikeReveal: Unlocking Temporal Sequences from Real Blurry Inputs with Spike Streams]]
- [[Towards full-stack deep learning-empowered data processing pipeline for synchrotron tomography experiments]]
- [[Towards Robust Event-guided Low-Light Image Enhancement: A Large-Scale Real-World Event-Image Dataset and Novel Approach]]
- [[3D Gaussian Splatting: Survey, Technologies, Challenges, and Opportunities]]
- [[DeblurSplat: SfM-free 3D Gaussian Splatting with Event Camera for Robust Deblurring]]
- [[Event Cameras Meet SPADs for High-Speed, Low-Bandwidth Imaging]]
- [[Event-guided temporally super-resolved synchrotron X-ray imaging]]
- [[EvSTVSR: Event Guided Space-Time Video Super-Resolution]]
- [[Dynamic EventNeRF: Reconstructing General Dynamic Scenes from Multi-view Event Cameras]]
- [[The interplay between events and frames: A comprehensive explanation]]
