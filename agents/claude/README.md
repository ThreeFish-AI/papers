# Claude Agents for Agentic AI Papers

This directory contains agents built using the Claude Agent SDK for processing Agentic AI research papers.

## Available Agents

### Paper Translation Agent
- **Purpose**: Translates English Agentic AI papers to high-quality Chinese
- **Input**: PDF/Web format papers
- **Output**: Markdown format with preserved structure and formatting

### Paper Extraction Agent
- **Purpose**: Extracts content from PDF papers and converts to Markdown
- **Features**:
  - Preserves mathematical formulas and tables
  - Extracts images and figures
  - Maintains citation structure

### Paper Analysis Agent
- **Purpose**: Analyzes and summarizes key insights from papers
- **Features**:
  - Extracts main contributions
  - Identifies key methodologies
  - Generates structured summaries

## Usage

Each agent can be run independently or as part of a pipeline:

```bash
# Run extraction agent
python extract_agent.py --input "paper.pdf" --output "extracted.md"

# Run translation agent
python translate_agent.py --input "extracted.md" --output "translated.md" --target "zh"

# Run analysis agent
python analyze_agent.py --input "translated.md" --output "analysis.md"
```

## Configuration

Agents can be configured through:
- Environment variables
- Configuration files in `config/`
- Command-line arguments

## Dependencies

- claude-agent-sdk
- pypdf2
- markdown
- requests