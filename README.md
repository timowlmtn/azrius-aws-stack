# Azrius GeoView Stack

**Azrius GeoView** is a serverless AWS deployment framework designed to ingest, process, and manage geotagged images and structured data through an event-driven pipeline. It uses CloudFormation, S3, SNS, SQS, and Lambda—configured for rapid deployment and teardown—making it a solid foundation for AI-powered image workflows such as scene understanding, object detection, or environmental diagnostics.

This project is part of the **Azrius Analytics** suite and serves as a modular backend for camera-based AI assistants.

---

## 🔧 What It Does

- **Auto-deploys** a serverless pipeline via CloudFormation
- **Packages and uploads** Lambda handlers to S3
- **Wires up triggers** between S3, SNS, SQS, and Lambda
- **Archives or tears down** entire environments cleanly
- **Syncs project data** to user-specific S3 prefixes
- **Enables model-based processing** using AWS Bedrock or your own endpoints

---

## 📁 Project Structure

```text
  web/app/aws/
  └── azrius-geovision/
  ├── lambda/ # Contains your Lambda handler.py
  ├── stack/ # CloudFormation YAML template
  ├── s3/ # Default data structure to sync to S3
  └── Makefile # Deployment automation
`

---

## ⚙️ Prerequisites

- AWS CLI configured with sufficient permissions (CloudFormation, S3, Lambda, SNS, SQS)
- Environment variables set:
  - `AZRIUS_APP_BUCKET`
  - `AZRIUS_APP_FOLDER`
  - `AZRIUS_APP_SNS`
  - `AZRIUS_APP_SQS`
  - `AZRIUS_APP_LAMBDA`
  - `AZRIUS_APP_PYTHON`
  - `AZRIUS_APP_REGION`
  - `AZRIUS_APP_MODEL_ARN`
  - `S3_DEPLOYMENT_BUCKET`

---

## 🚀 Usage

### 🔁 Full Stack Deployment

```bash
make deploy

## ✅ Example Use Case
This project is ideal for use cases such as:

Camera-based AI agents that upload field photos to S3

Automatically triggered processing with Bedrock, OpenCV, or custom logic

GIS and environmental monitoring applications

Lightweight, event-driven ML pipelines without the overhead of managed orchestration

## 👩‍💻 Contributing
Feel free to fork, PR, or adapt this stack for your own projects. If you use this to deploy an AI agent or data pipeline, let us know!

## 🧠 About Azrius
Azrius Analytics builds AI-powered tools that help teams automate data governance, optimize costs, and integrate intelligence into spreadsheets, images, and structured workflows.

Visit us at azri.us
