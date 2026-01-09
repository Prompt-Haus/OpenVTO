# OpenVTO Examples

Runnable examples demonstrating OpenVTO's virtual try-on capabilities.

## Prerequisites

```bash
pip install openvto
```

## Google Vertex AI Setup

1. Set up a Google Cloud project and enable the Vertex AI API.
2. Create a service account and download the JSON key file.
3. Set the following environment variables:

```bash
export GOOGLE_SERVICE_ACCOUNT_KEY="path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

## Examples

**Jupyter notebook:** `basic_workflow.ipynb` — Interactive walkthrough with visualizations.
