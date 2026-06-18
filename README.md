# EIA Reproducible Modeling Framework: Field Production Utility

A lightweight Python pipeline designed to process granular, field-level energy telemetry, execute asset status classification rules, and generate structured macro basin production summaries. 

This repository serves as a clean, reproducible engineering blueprint for handling structural data validation and pipeline normalization across multi-fluid asset layers.

## Features
* **Dynamic Schema Mapping:** Automatically detects and conforms varying column structures (e.g., official public basin exports vs. localized internal schemas).
* **Volumetric Status Classification:** Evaluates rolling total output metrics to programmatically categorize fields into distinct operational states (`Active Co-Production`, `Pure Oil`, `Pure Gas`, or `Shut-In / Suspended`).
* **Performance Scoring:** Implements automated, fault-tolerant Gas-to-Oil Ratio (GOR) tracking and Barrels of Oil Equivalent (BOE) conversions.
* **Environment Isolation Safeguard:** Features an automated mock telemetry fallback engine to guarantee 100% processing and testing uptime if local production source files are decoupled.

## Project Structure
* `nsta_field_classifier.py`: Core executable pipeline script.
* `requirements.txt`: Minimalist environment dependency manifest.
* `.gitignore`: Project sandbox exclusions safeguarding virtual environments and data binaries.

## Getting Started

### 1. Initialize Isolated Sandbox
```bash
python -m venv venv
source venv/Scripts/activate  # On macOS/Linux: source venv/bin/activate
pip install -r requirements.txt