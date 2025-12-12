# Google ADK Agents for Agentic AI Papers

This directory contains agents built using Google's Agent Development Kit (ADK) for processing Agentic AI research papers.

## Available Agents

### PDF Processing Agent
- **Purpose**: Advanced PDF processing with OCR and layout preservation
- **Features**:
  - High-quality text extraction
  - Table and figure detection
  - Multi-language support

### Batch Translation Agent
- **Purpose**: Batch processing of multiple papers for translation
- **Features**:
  - Parallel processing
  - Progress tracking
  - Error handling and retry logic

### Metadata Extraction Agent
- **Purpose**: Extracts structured metadata from papers
- **Features**:
  - Author information
  - Publication details
  - Citation network analysis
  - Keyword extraction

## Setup

1. Install Google ADK:
```bash
pip install google-adk
```

2. Configure authentication:
```bash
gcloud auth application-default login
```

## Usage

```bash
# Run PDF processing
adk run pdf_processor --input "papers/source/" --output "processed/"

# Run batch translation
adk run batch_translator --config "config/translation.yaml"

# Run metadata extraction
adk run metadata_extractor --input "paper.pdf" --format "json"
```

## Configuration

Configuration files are located in `config/`:
- `pdf_processing.yaml` - PDF processing settings
- `translation.yaml` - Translation parameters
- `metadata.yaml` - Metadata extraction rules

## Performance

- Supports GPU acceleration for PDF processing
- Distributed processing for large batches
- Optimized for academic paper formats