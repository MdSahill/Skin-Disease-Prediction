# 🩺 Skin Disease Classification Web App

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red)](https://pytorch.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0-lightgrey)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

![Demo GIF](static/images/demo.gif) *(Add your demo.gif to /static/images/)*

## 🏗️ System Architecture

```mermaid
graph TD
    A[User Interface] -->|Upload Image| B[Flask Server]
    B -->|Preprocess| C[ResNet Model]
    C -->|Prediction| D[Results Display]
    D --> E[Confidence Visualization]
    
    subgraph Backend
        B --> F[Image Normalization]
        F --> G[224x224 Resize]
    end
    
    subgraph AI Model
        C --> H[Residual Blocks]
        H --> I[Global Pooling]
        I --> J[22-class Classifier]
    end
