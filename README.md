# V.O.R.T.I.C.E.

### Volumetric Optical Reality Tracking & Immersive Computational Environment
> @ Aldair Humberto Martinez Willians

![Status](https://img.shields.io/badge/Status-In%20Development-yellow) 
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![OpenGL](https://img.shields.io/badge/OpenGL-4.6-green.svg)](https://www.opengl.org/)
[![PyQt5](https://img.shields.io/badge/PyQt-5.15-orange.svg)](https://www.riverbankcomputing.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ✨ Description
**Volumetric Optical Reality Tracking & Immersive Computational Environment (V.O.R.T.I.C.E.)** represents a paradigmatic leap in the visualization and manipulation of immersive data. It is a third-generation holographic interface that transcends the boundaries of traditional visualization, transforming images, documents and data sets into transparent, interactive cubes that come to life in three-dimensional space, manipulable in real time with imperceptible latency. Designed for environments where visual understanding and intuitive interaction are critical — from business intelligence and data analytics to architectural visualization and educational environments — **V.O.R.T.I.C.E.** turns static information into dynamic, explorable experiences.

**Octopus Neuroarchitecture**: Biomimetic Parallel Processing The system finds its inspiration in one of nature's most efficient designs: octopus neuroarchitecture. This cephalopod has a central brain that coordinates intention, while seven peripheral brains distributed in its arms process sensory information and execute actions autonomously and simultaneously. Applying this biological principle to computational processing, **V.O.R.T.I.C.E.** implements a distributed computing architecture

- **Central Brain (Orchestrator)**: Manages the 3D spatial rendering in OpenGL, coordinates the global state of the holographic cubes, and synchronizes real-time visual library tree navigation.

- **7 Peripheral Brains (Parallel Workers)**: Dedicated sub-processes handling image processing, real-time matrix transformations (night vision, infrared, negative filters), and optical/gestural tracking without impacting the main frame rate.

---

## 🎯 The Problem: The Icon is the Epitaph of an Agonizing Digital Age
We live surrounded by visual information, but we continue to interact with it through flat lists, static grids, and icons that do not communicate the richness of real content. The way we view photos, videos and documents is anchored in paradigms of the last century. The double click to open, look and close is an outdated ritual that turns browsing into a passive and fragmented act, where 80% of time is wasted on search and only 20% on true analysis. 
The future has already arrived, but we continue to see it through the lenses of the past. The traditional interface is a filter that hides relationships, hierarchies, and semantic connections between data, limiting our ability to understand complexity.


## 🔭 The Vision: From Icon to Holographic Experience
Imagine an environment where multimedia is not stored in lists, but floats in three-dimensional space like tangible objects that you can:

- **Observe from any angle**: without orientation restrictions, seeing each image in its maximum splendor.
- **Organize hierarchically**: in a cognitive tree that replicates the natural structure of your thinking, connecting ideas through semantic relationships.
- **Manipulate in real time**: dragging, turning and climbing as if you were holding a physical object in your hands.
- **Filter and transform**: applying visual effects such as night, thermal or infrared vision to extract information invisible to the naked eye.
- **Contextualize multiple elements simultaneously**: to identify patterns that would go unnoticed in 2D, discovering connections that flat interfaces hide.

## 🎯 ¿For whom and for what?
Researchers and analysts who need to visualize multiple graphs and data in a connected 3D environment, identifying relationships not evident on flat screens. Doctors layering diagnostic images for holistic comparison. Architects and designers who explore renders, plans and references in an immersive space that allows you to visualize the project before building it. Educators presenting multimedia content in an environment that students can actively explore, increasing retention. Data scientists visualizing multidimensional datasets where correlations become evident. 
**V.O.R.T.I.C.E.** is for anyone who understands that information is not flat: it has relationships, hierarchies and connections that lists hide and that only an immersive environment can reveal.

## 🚀 The Technological Leap: Principles of Cognitive Design
- **Spatial Coding**: The human brain is optimized to navigate 3D spaces. VORTICE takes advantage of this innate ability, reducing cognitive load and accelerating understanding. 
- **Visual Hierarchical Relationships**: The cube tree reflects how the brain organizes knowledge: general concepts → categories → specific elements, facilitating contextual navigation. 
- **Immediate Visual Feedback**: Manipulation in real time with imperceptible latency, creating a feeling of presence and direct control over the information. 
- **Visual Multimodality**: Real-time filters to extract different layers of information from the same source, revealing data that remains hidden in traditional visualization.

---

## 🧠 Architecture
Applied Design Principles:
- **Clean Architecture**: Clear separation between UI, business logic and infrastructure
- **Dependency Inversion**: Abstractions that decouple modules and facilitate testing
- **Single Responsibility**: Each module has a unique and well-defined purpose
- **Open/Closed Principle**: Extendable without modifying existing code

```bash
               +----------------------------------+
               |    CENTRAL BRAIN (Orchestrator)  |
               |   OpenGL 3D / State / Interface  |
               +----------------------------------+
                              |
     +------------------------+----------------------------+
     |                        |                            |
[Brain 1]                 [Brain 2]                   [Brains 3-7]
MediaPipe Tracking       OpenCV (cv2)                Optical Filters
(Gesture Capture)       (Data & Image Ingestion)    (Night, Thermal, Invert)
```

## 🛠 Technical Stack
- Language: **Python 3.10+**
- Rendering & Graphic Engine: **PyOpenGL / OpenGL ES**
- Computer Vision & Tracking: **OpenCV (cv2), MediaPipe**
- Parallel Computing: **multiprocessing / concurrent.futures**

## 📂 Project structure
```bash
vortice-3d-reality/
├── src/
│   ├── core/
│   │   ├── orchestrator.py     # Main window ("Central Brain")
│   │   ├── tree_manager.py     # Cube tree logic
│   │   ├── cube_node.py        # Individual tree node
│   │   └── multiprocessing.py  # Simulation of the 8 "brain" bars
│   ├── vision/
│   │   ├── filters.py          # OpenCV filters (gray, negative, thermal...)
│   │   └── tracker.py          # Stub for future gestures (NOT implemented)
│   ├── render/
│   │   ├── renderer.py         # OpenGL (HolographicWidget) engine
│   │   ├── camera.py           # Orbital camera (mouse/keyboard)
│   │   └── gradients.py        # Mathematical gradient backgrounds
│   └── utils/
│       ├── config.py           # Constants and style sheet
│       └── logger.py           # Structured logging
├── tests/
│   ├── unit/                   # Filter tests
│   └── integration/            # Tree tests + render
├── docs/
│   ├── ARCHITECTURE.md
│   └── GESTURE_CONTROLS.md
├── main.py                     # Entry point
└── requirements.txt
```

## 🚀 Installation
```bash
# Clone the repository
git clone https://github.com/AldairMaWill/vortice-3d-reality.git
cd vortice-3d-reality

# Create and activate virtual environment (Recommended)
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## ▶ Usage
```bash
# Launch the orchestration engine and 3D holographic interface
python main.py
```

## Controles

| Acción | Control |
|---|---|
| Rotar cámara | Click izquierdo + arrastrar |
| Mover cámara | Click central + arrastrar, o flechas |
| Zoom | Rueda del mouse |
| Seleccionar siguiente cubo | Click derecho o Espacio |
| Reset de vista | Tecla `R` |
| Alternar grid | Tecla `G` |
| Alternar ejes | Tecla `A` |
| Alternar bordes de cubos | Tecla `E` |

## 🗺 Roadmap
- [ ] Integration with Leap Motion sensors for ultra-high precision gesture tracking.
- [ ] Pipeline optimization via CUDA / PyCUDA for dedicated GPU acceleration across peripheral brains.
- [ ] Export module for 3D node maps to Augmented Reality (AR/VR) formats.

## 📄 License
MIT @ AMW 
> @ Aldair Humberto Martinez Willians 
