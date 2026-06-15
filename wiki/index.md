# Research Wiki

这是从本地 Zotero PDF 自动生成、再逐步人工迭代的 Obsidian-style research wiki。它的目标不是替代精读，而是把几百篇论文沉淀成可导航、可追问、可扩展的研究地图。

## Dashboard

- Paper summaries: 587
- Concept pages: 13
- Method pages: 8
- Dataset pages: 18
- Open problem pages: 1

## How To Use This Wiki

1. 从下面的 `Research Map` 进入一个主题，而不是从 587 篇论文逐篇翻。
2. 在概念页或方法页里看 `Paper Mentions`，找到高频论文和交叉方向。
3. 把真正精读后的判断写回概念页的 `Summary`、`Key Questions` 或新建 `research_ideas/` 页面。
4. Zotero 新增论文后运行 `python scripts/ingest_zotero.py --max-pages 12` 和 `python scripts/update_wiki.py` 刷新索引。

## Research Map

### Event-based Sensing and Neuromorphic Vision

- Core concepts: [Event Camera](concepts/event-camera.md), [Neuromorphic Vision](concepts/neuromorphic-vision.md)
- Closely related methods: [Deblurring](methods/deblurring.md), [Image Restoration](methods/image-restoration.md)
- Typical questions: event streams for deblurring, HDR, frame interpolation, optical flow, 3D reconstruction, and low-latency sensing.

### X-ray CT, Tomography, and Dynamic Imaging

- Core concepts: [Tomography](concepts/tomography.md), [X-ray CT](concepts/x-ray-ct.md), [Dynamic Imaging](concepts/dynamic-imaging.md), [4D Imaging](concepts/4d-imaging.md)
- Closely related methods: [Tomography](methods/tomography.md), [Sparse-view Reconstruction](methods/sparse-view-reconstruction.md), [Neural Field](methods/neural-field.md)
- Typical questions: sparse-view CT, limited-angle reconstruction, dynamic/4D tomography, synchrotron imaging, physics-informed reconstruction, and beamline data processing.

### Neural Representations and Gaussian Splatting

- Core concepts: [Neural Field](concepts/neural-field.md), [Implicit Neural Representation](concepts/implicit-neural-representation.md), [Gaussian Splatting](concepts/gaussian-splatting.md)
- Closely related methods: [Gaussian Splatting](methods/gaussian-splatting.md), [Implicit Neural Representation](methods/implicit-neural-representation.md), [Diffusion Model](methods/diffusion-model.md)
- Typical questions: continuous scene/volume representation, 3DGS for CT, radiative Gaussian splatting, NeRF/INR baselines, dynamic view synthesis, and physical consistency.

### Restoration, Priors, and Generative Models

- Core concepts: [Deblurring](concepts/deblurring.md), [Image Restoration](concepts/image-restoration.md), [Diffusion Model](concepts/diffusion-model.md)
- Closely related methods: [Deblurring](methods/deblurring.md), [Image Restoration](methods/image-restoration.md), [Diffusion Model](methods/diffusion-model.md)
- Typical questions: learned priors, event-guided restoration, low-light/HDR recovery, super-resolution, denoising, and diffusion priors for inverse problems.

## High-Signal Intersections

- [Event Camera](concepts/event-camera.md) x [Gaussian Splatting](concepts/gaussian-splatting.md): event-aided 3D reconstruction, deblurring, and novel view synthesis.
- [X-ray CT](concepts/x-ray-ct.md) x [Gaussian Splatting](concepts/gaussian-splatting.md): radiative Gaussian representations and sparse-view tomographic reconstruction.
- [Tomography](concepts/tomography.md) x [Neural Field](concepts/neural-field.md): implicit continuous reconstruction, dynamic CT, and physics-informed neural fields.
- [Dynamic Imaging](concepts/dynamic-imaging.md) x [4D Imaging](concepts/4d-imaging.md): time-resolved acquisition, motion modeling, and continuous-time reconstruction.
- [Diffusion Model](concepts/diffusion-model.md) x [Sparse-view Reconstruction](methods/sparse-view-reconstruction.md): generative priors for underdetermined inverse problems.

## Suggested Reading Routes

### Route A: Event Cameras to 3D Reconstruction

1. [Event Camera](concepts/event-camera.md)
2. [Deblurring](methods/deblurring.md)
3. [Gaussian Splatting](methods/gaussian-splatting.md)
4. [Dynamic Imaging](concepts/dynamic-imaging.md)

### Route B: Sparse-view CT to Neural Reconstruction

1. [X-ray CT](concepts/x-ray-ct.md)
2. [Tomography](methods/tomography.md)
3. [Sparse-view Reconstruction](methods/sparse-view-reconstruction.md)
4. [Neural Field](methods/neural-field.md)
5. [Gaussian Splatting](methods/gaussian-splatting.md)

### Route C: Dynamic 4D Imaging

1. [Dynamic Imaging](concepts/dynamic-imaging.md)
2. [4D Imaging](concepts/4d-imaging.md)
3. [Tomography](concepts/tomography.md)
4. [Image Restoration](methods/image-restoration.md)

## Most Connected Pages

### Concepts

- [Tomography](concepts/tomography.md) - 199 linked papers
- [Event Camera](concepts/event-camera.md) - 129 linked papers
- [Deblurring](concepts/deblurring.md) - 83 linked papers
- [Gaussian Splatting](concepts/gaussian-splatting.md) - 50 linked papers
- [X-ray CT](concepts/x-ray-ct.md) - 35 linked papers
- [Implicit Neural Representation](concepts/implicit-neural-representation.md) - 28 linked papers
- [Neural Field](concepts/neural-field.md) - 26 linked papers
- [Image Restoration](concepts/image-restoration.md) - 24 linked papers

### Methods

- [Tomography](methods/tomography.md) - 199 linked papers
- [Deblurring](methods/deblurring.md) - 83 linked papers
- [Gaussian Splatting](methods/gaussian-splatting.md) - 50 linked papers
- [Implicit Neural Representation](methods/implicit-neural-representation.md) - 28 linked papers
- [Neural Field](methods/neural-field.md) - 26 linked papers
- [Image Restoration](methods/image-restoration.md) - 24 linked papers
- [Diffusion Model](methods/diffusion-model.md) - 18 linked papers
- [Sparse-view Reconstruction](methods/sparse-view-reconstruction.md) - 15 linked papers

### Datasets

- [AAPM](datasets/aapm.md) - 5 linked papers
- [D-NeRF](datasets/d-nerf.md) - 5 linked papers
- [DAVIS](datasets/davis.md) - 4 linked papers
- [GoPro](datasets/gopro.md) - 3 linked papers
- [Blender](datasets/blender.md) - 2 linked papers
- [BS-ERGB](datasets/bs-ergb.md) - 2 linked papers
- [DSEC](datasets/dsec.md) - 2 linked papers
- [DyNeRF](datasets/dynerf.md) - 2 linked papers

## Maintenance Loop

```powershell
cd "C:\Users\wang_h3\Documents\personal page"
python scripts\ingest_zotero.py --max-pages 12
python scripts\update_wiki.py
git add wiki scripts templates README.md .gitignore
git commit -m "Update research wiki"
git push origin main
```

## Quality Notes

- `wiki/papers/` 里的单篇页是 public-safe 自动摘要，只保存元数据、关键词级信号和 Obsidian 链接，不保存 PDF 全文或大段原文。
- 概念页、方法页和数据集页是自动链接骨架。真正有价值的 synthesis 应该逐步人工写入 `Summary`、`Key Questions` 和 `research_ideas/`。
- `open_problems/extracted-open-problems.md` 是候选池，不是最终研究问题清单。需要人工合并、改写和去噪。

## Sections

- [Paper index](papers/index.md)
- [Concepts](#concepts)
- [Methods](#methods)
- [Datasets](#datasets)
- [Open Problems](#open-problems)
- [Research ideas](research_ideas/)

## Concepts

- [4D Imaging](concepts/4d-imaging.md)
- [Deblurring](concepts/deblurring.md)
- [Diffusion Model](concepts/diffusion-model.md)
- [Dynamic Imaging](concepts/dynamic-imaging.md)
- [Event Camera](concepts/event-camera.md)
- [Gaussian Splatting](concepts/gaussian-splatting.md)
- [Image Restoration](concepts/image-restoration.md)
- [Implicit Neural Representation](concepts/implicit-neural-representation.md)
- [Neural Field](concepts/neural-field.md)
- [Neuromorphic Vision](concepts/neuromorphic-vision.md)
- [Sparse-view Reconstruction](concepts/sparse-view-reconstruction.md)
- [Tomography](concepts/tomography.md)
- [X-ray CT](concepts/x-ray-ct.md)

## Methods

- [Deblurring](methods/deblurring.md)
- [Diffusion Model](methods/diffusion-model.md)
- [Gaussian Splatting](methods/gaussian-splatting.md)
- [Image Restoration](methods/image-restoration.md)
- [Implicit Neural Representation](methods/implicit-neural-representation.md)
- [Neural Field](methods/neural-field.md)
- [Sparse-view Reconstruction](methods/sparse-view-reconstruction.md)
- [Tomography](methods/tomography.md)

## Datasets

- [AAPM](datasets/aapm.md)
- [Blender](datasets/blender.md)
- [BS-ERGB](datasets/bs-ergb.md)
- [CIFAR10-DVS](datasets/cifar10-dvs.md)
- [COCO](datasets/coco.md)
- [D-NeRF](datasets/d-nerf.md)
- [DAVIS](datasets/davis.md)
- [DeepLesion](datasets/deeplesion.md)
- [DSEC](datasets/dsec.md)
- [DTU](datasets/dtu.md)
- [DyNeRF](datasets/dynerf.md)
- [GoPro](datasets/gopro.md)
- [HyperNeRF](datasets/hypernerf.md)
- [ImageNet](datasets/imagenet.md)
- [JIGSAWS](datasets/jigsaws.md)
- [LIDC](datasets/lidc.md)
- [LLFF](datasets/llff.md)
- [Mayo](datasets/mayo.md)

## Open Problems

- [Extracted Open Problems](open_problems/extracted-open-problems.md)
