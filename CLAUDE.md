# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a research repository focused on AI Agents papers, containing translated academic papers, summaries, and research materials in Chinese and English. The repository is organized around key research areas in AI agents, context engineering, and retrieval-augmented generation.

## Directory Structure

```
papers/
├── Context Engineering/    # Context Engineering 2.0 research and translations
├── DeepSeek OCR/           # DeepSeek OCR paper translation
├── GraphRAG/               # Graph-Guided Retrieval-Augmented Generation papers
├── LLM Agents/             # LLM Agents survey papers and translations
├── .claude/                # Claude Code configuration
├── .assets/                # Static resources and images
├── AGENTS.md               # AI Agents paper translation guidelines
└── README.md               # Repository overview
```

## Core Research Areas

### 1. Context Engineering (上下文工程)
- **Key Paper**: "Context Engineering 2.0: The Context of Context Engineering"
- **Focus**: Historical evolution of context engineering from 1.0 to 4.0 eras
- **Content**: Complete Chinese translation with diagrams and summaries
- **Location**: `Context Engineering/Qwen-摘要.md`

### 2. LLM Agents Survey
- **Key Paper**: "Empowering Real-World: A Survey on the Technology, Practice, and Evaluation of LLM-driven Industry Agents"
- **Focus**: Industry applications, technology foundations, and evaluation methods
- **Framework**: 5-level capability maturity model for industry agents
- **Core Technologies**: Memory, Planning, Tool Use
- **Location**: `LLM Agents/Empowering Real-World: A Survey...md`

### 3. GraphRAG Research
- **Key Papers**:
  - "Graph-Guided Concept Selection for Efficient Retrieval-Augmented Generation"
  - "Knowledge graphs: Introduction, history, and perspectives"
- **Focus**: Optimizing GraphRAG costs through concept selection
- **Location**: `GraphRAG/愫读.md`, `GraphRAG/愫读-2.md`

### 4. DeepSeek OCR
- **Key Paper**: "DeepSeek-OCR: Contexts Optical Compression"
- **Focus**: OCR technology and context compression
- **Location**: `DeepSeek OCR/DeepSeek_OCR_paper_中文版.md.md`

## File Organization Standards

### Paper Translation Process
1. **Original PDFs**: Stored in respective directories (ignored by git)
2. **Chinese Translations**: Named with `中文版.md` suffix
3. **Summaries**: Use `愫读.md` or `摘要.md` prefixes
4. **Images**: Stored in `images/` subdirectories with relative paths

### Translation Guidelines (from AGENTS.md)
When handling papers beyond reasonable scope:
- **Section-based translation**: Translate specific parts (abstract, introduction, figures)
- **Full overview**: Provide comprehensive Chinese summaries
- **Key content focus**: Core concepts, definitions, design considerations

## Development Workflow

### Adding New Papers
1. Create dedicated directory for paper topic
2. Add original PDF (automatically ignored by git)
3. Create Chinese translation with appropriate naming
4. Add summary/analysis files using established naming conventions
5. Update directory structure documentation

### Translation Best Practices
- Maintain original formatting and structure
- Include figure descriptions and table summaries
- Preserve technical terminology accuracy
- Add contextual explanations where needed for Chinese readers

### Git Configuration
- **Allowed commands**: `git pull:*`, `git add:*`, `git commit:*`, `tree:*`
- **Ignored files**: `.DS_Store`, `*.pdf` (source papers)
- **Permissions**: Configured in `.claude/settings.local.json`

## Content Standards

### Academic Translation Approach
- **Precision**: Maintain technical accuracy in translations
- **Readability**: Adapt academic language for Chinese readers while preserving scholarly tone
- **Completeness**: Include all key sections, figures, tables, and references
- **Context**: Provide necessary cultural and technical context for Chinese audience

### File Naming Conventions
- **Full Translations**: `[Paper Name]_中文版.md.md`
- **Summaries**: `愫读.md`, `摘要.md`, `Qwen-摘要.md`
- **Documentation**: `GRAPH.md` for comprehensive topic overviews
- **Images**: Descriptive names with relative path references

## Research Integration

This repository serves as a comprehensive resource for:
- **Academic Research**: Translated papers for Chinese-speaking researchers
- **Technology Assessment**: Comparative analysis of different AI agent approaches
- **Implementation Guidance**: Practical insights from industry surveys
- **Historical Context**: Evolution of context engineering and related technologies

The content emphasizes bridging theoretical research with practical industry applications, particularly focusing on the maturity frameworks and evaluation methodologies for real-world AI agent deployment.