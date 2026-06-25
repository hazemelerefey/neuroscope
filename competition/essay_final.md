# Project Introduction — NeuroScope

**Project Name:** NeuroScope — AI-Powered 3D Neural Network Architecture Visualizer and Analyzer

**Team Name:** DigiNeurons

**Category:** Education Enhancement

**Competition:** AYAIR 2026 — Third Edition

**Submitted by:** DigiNeurons (Team of 5)

**Date:** June 2026

---

## The Problem

Every year, millions of students across Africa begin learning deep learning. They learn to train models, achieve high accuracy scores, and deploy applications. But beneath this surface lies a critical gap: most students cannot explain what happens inside the architectures they build. They copy structures from repositories without understanding why a ResNet uses skip connections or why a transformer relies on multi-head attention. When models fail, they cannot diagnose the issue. The network is a black box — they can operate it but never see inside it.

This gap is especially harmful in Africa. Egypt's Ministry of Communications has made digital transformation a national priority. The African Union's Agenda 2063 and STISA 2034 strategy call for technically skilled youth to lead the continent's digital industrialization. Yet the tools available to these students were not designed for them. Existing visualizers show only static diagrams, offer no explanation, and provide no feedback on architectural mistakes. None of them work offline on a smartphone.

## Our Solution

NeuroScope is a web-based application and Visual Studio Code extension that transforms how students learn deep learning by making neural network architectures visible, interactive, and understandable. Developed by the DigiNeurons team — Hazem Khaled, Amr Mahmoud, Shahd Khairy, Yomna Ashraf, and Yossef Sharif — NeuroScope bridges the gap between writing code and truly understanding it.

A student uploads a model file — supporting ONNX, PyTorch, Keras, and TensorFlow Lite formats — or opens a Python script. NeuroScope parses the code and generates an interactive three-dimensional visualization. Convolutional layers appear as geometric shapes, fully connected layers as flat planes, and attention mechanisms as distinct structures. Clicking any component reveals a plain-language description of its function, the code that created it, and key metrics including parameters, FLOPs, and memory usage.

The architecture health check engine detects over forty-seven common anti-patterns: missing activation functions, sigmoid in deep networks, parameter explosion, redundant layers, and more. Each finding includes severity, explanation, and a suggested fix — functioning as a spell-checker for neural network design.

Real-time simulation updates the three-dimensional view instantly when a student edits code, before execution. Changing filter counts or adding layers immediately shows architectural impact. When the student runs their code, NeuroScope animates the forward pass: data flows as animated particles, tensor shapes transform at each layer, and the student watches input become prediction.

## How It Works

NeuroScope integrates into a student's existing workflow through two entry points. The VS Code extension provides inline feedback directly in the code editor. The web application runs entirely in the browser with no installation required. As a progressive web application, it functions offline — critical for areas with intermittent connectivity. It requires no GPU, no cloud credits, and no expensive licenses. It runs on smartphones, tablets, or older laptops.

The tool supports five languages: English, French, Arabic, Swahili, and Portuguese — reaching Egypt's Arabic-speaking communities, Francophone West and Central Africa, East Africa's Swahili-speaking regions, and Lusophone Southern Africa. This multilingual approach ensures that language is never a barrier to understanding deep learning.

## Impact

NeuroScope directly addresses the mentorship gap in African AI education. When no senior engineer is available to review a student's architecture, NeuroScope provides that review automatically. It aligns with the AU's STISA 2034 priority of building scientific literacy, with Agenda 2063's vision of inclusive development, and with Egypt's national digital transformation strategy.

This tool serves students worldwide. Every learner who struggles to understand why their network is not learning, or what each component in a transformer does, benefits from NeuroScope. By making architecture understanding accessible, we lower the barrier to meaningful participation in AI development.

## Sustainability

NeuroScope is released under the MIT license as a fully open-source project. University professors can integrate it into curricula. Students can contribute new analysis rules and translations. Institutions can deploy their own instances. We are building NeuroScope not just as a competition entry, but as lasting infrastructure for deep learning education across Africa and beyond.

---

**Word Count: 637**
