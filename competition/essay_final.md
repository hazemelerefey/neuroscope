# Project Introduction — NeuroScope

**Project Name:** NeuroScope — AI-Powered 3D Neural Network Architecture Visualizer and Analyzer

**Team Name:** DigiNeurons

**Category:** Education Enhancement

**Competition:** The Third Edition of the Presidential African Youth in Artificial Intelligence and Robotics Competition 2026 (AYAIR)

**Submitted by:** Hazem Khaled Ezzat Abdel Halim

**Date:** June 2026

---

## The Problem We Solve

Millions of students across Africa and the world begin their journey into deep learning each year. They enroll in courses, attend university programs, and learn to write code like `model.fit()` to achieve high accuracy scores. But beneath this surface-level success lies a fundamental gap: **most students do not understand what happens inside the models they build.**

They copy architectures from GitHub without knowing why a ResNet uses skip connections, or why a transformer uses multi-head attention, or why batch normalization stabilizes training. When their model fails, they cannot diagnose the problem. The model is a black box — they can operate it, but they cannot see inside it.

This problem is especially acute in Africa. Egypt's Ministry of Communications and Information Technology has made digital transformation a national priority. Nigeria, Kenya, South Africa, Rwanda, and Tunisia are investing heavily in AI education. The African Union's Agenda 2063 and STISA 2034 strategy call for technically skilled youth to lead Africa's digital industrialization.

But the tools available to these students were not designed for them. Netron shows static two-dimensional diagrams with no explanation. TensorBoard is locked to TensorFlow and requires running training first. TensorSpace.js, which once offered three-dimensional visualization, has been abandoned since 2019. None of these tools explain what a layer does, detect architectural mistakes, work offline on a phone, or connect the visualization back to the student's actual code.

**NeuroScope changes this.**

## Our Solution

NeuroScope is a web-based tool and Visual Studio Code extension that transforms how students learn deep learning by making neural network architectures visible, interactive, and understandable.

A student uploads their model file — ONNX, PyTorch, Keras, or TensorFlow Lite — or opens their Python script or Jupyter notebook. NeuroScope parses the code and generates a **three-dimensional interactive visualization** of the architecture. Convolutional layers appear as boxes, fully connected layers as flat planes, recurrent layers as cylinders, and attention layers as octahedrons.

**Clicking any three-dimensional component** shows three things: a plain-language description of what that layer does, the exact code block that created it, and the layer's parameters, FLOPs, and memory footprint. This bidirectional mapping means a student can explore a transformer in 3D and understand the code, or read code and see the architecture.

**The architecture health check engine** detects over forty-seven common anti-patterns: missing activation functions, sigmoid in deep networks, missing skip connections, parameter explosion, redundant layers, and more. Each finding includes severity, explanation, and a suggested fix — like a spell-checker for neural network design.

**The real-time simulation** updates the three-dimensional visualization instantly when a student edits code — before running it. Changing the number of filters, adjusting dropout, or adding a layer immediately shows the architectural impact, developing intuition that would otherwise require months of trial and error.

**When the student runs their code**, NeuroScope animates the forward pass: data flows through the network as animated particles, tensor shapes change at each layer, and the student watches input transform into a prediction in real time.

## Impact for Africa and the World

NeuroScope is free, open-source, and designed for the environments where it is needed most. It works entirely in the browser with no installation. It functions as a progressive web application that works offline — critical for areas with intermittent connectivity. It requires no GPU, no cloud credits, and no expensive licenses. It runs on a smartphone, a tablet, or a ten-year-old laptop.

It supports five languages: English, French, Arabic, Swahili, and Portuguese — covering Egypt's Arabic-speaking governorates, Francophone West and Central Africa, East Africa's Swahili-speaking regions, and Lusophone Southern Africa.

NeuroScope aligns with the AU's STISA 2034 priority of building scientific literacy, with Agenda 2063's call for inclusive development, and with Egypt's national digital transformation strategy. It addresses the mentorship gap: when no senior ML engineer is available to review a student's architecture, NeuroScope provides that review automatically and clearly.

But this tool is not only for Africa. Every student worldwide who struggles to understand why their network is not learning, or what each block in a transformer does, will benefit from NeuroScope.

## Sustainability

NeuroScope is released under the MIT license as a fully open-source project. University professors can integrate it into curricula, students can contribute new analysis rules and translations, and institutions can deploy their own instances. We are building NeuroScope not just as a competition entry, but as lasting infrastructure for deep learning education in Africa and beyond.
