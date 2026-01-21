# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based system for analyzing sales meeting transcripts using Claude AI with extended context (1M tokens). The system creates digital profiles of employees and analyzes meeting effectiveness using a custom Memory Tool implementation.

**Core Functionality:**
- Digital profile generation from meeting transcripts
- Multi-threaded analysis of sales meeting databases
- Custom file-based memory management for Claude AI
- Sales analytics and conversion tracking

## Development Environment Setup

### Virtual Environment
```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Required in `.env` file:
- `CLAUDE_API` - Anthropic API key for Claude

## Key Architecture Components

### 1. MemoryTool System (MemoryTool.py)

Custom implementation of `BetaAbstractMemoryTool` that provides file system operations for Claude AI:

**Directory Structure:**
- `/memories/` - Writable directory for generated analyses, reports, and digital profiles
- `/transcripts/` - Read-only directory containing meeting transcripts (JSON format)

**Operations:**
- `view(path)` - Read files or list directories
- `create(path, file_text)` - Create new files (memories only)
- `delete(path)` - Delete files (memories only)
- `insert(path, insert_line, insert_text)` - Insert text at specific line
- `rename(path, new_path)` - Rename files (memories only)
- `str_replace(path, old_str, new_str)` - Replace unique text fragments (memories only)

**Important Constants:**
- `MODEL = "claude-sonnet-4-5-20250929"`
- `BETAS = ["context-1m-2025-08-07", "context-management-2025-06-27"]`

### 2. Main Analysis Scripts

**CreateDigitalProfile.py** - Generates detailed employee profiles from meeting transcripts
- Analyzes communication patterns, competencies, and Spiral Dynamics levels
- Processes all transcripts in `/transcripts/` for specified employees
- Outputs comprehensive profiles to `/memories/`

**query_handler_multithreaded.py** - Multi-threaded sales analytics engine
- Processes multiple analytical queries in parallel (default: 5 threads)
- Analyzes Demo2Pilots database with questions about conversion rates, channel effectiveness, manager performance
- Uses placeholder system for dynamic file naming: `[PLACEHOLDER1]`, `[PLACEHOLDER2]`

**helper_file.py** - Contains system prompts and configuration for analysis tasks

### 3. ClaudeClient (ClaudeClient.py)

Simple wrapper around Anthropic client:
```python
client = Client()
client.client  # Access to Anthropic client instance
```

## Running the System

### Generate Digital Profiles
```bash
python CreateDigitalProfile.py
```
Processes employee transcripts and creates personality/competency profiles.

### Run Multi-threaded Analytics
```bash
python query_handler_multithreaded.py
```
Executes 15 predefined analytical queries across sales meeting database using 5 parallel threads.

### Create Analytics Database
```bash
python CreateDigitalProfile.py
```
Generates `analytics_db.json` with aggregated meeting statistics, indexes, and insights.

## Data Model

### Meeting Transcript Structure (JSON)
Each transcript contains:
- `metadata` - Meeting details (ID, date, client, managers, channels, status)
- `criteria` - 17 evaluation criteria (1-10 scale or classification)
- `overall_summary` - Aggregated scores and conversion probability
- `manager_comments` - Subjective notes from sales managers

### Meeting Success Classification
- `meeting_success: "да"` - Successful (client agreed to next step)
- `meeting_success: "нет"` - Unsuccessful (client declined)
- `meeting_success: "непонятно"` - Neutral (decision pending)

### Critical Criterion: client_task_classification
**Not a 1-10 scale** - This is a fixed classification:
- `1` = Client came WITHOUT a task (exploratory)
- `2` = Client came WITH a specific task
- `3` = Insufficient data to classify

## Important System Behaviors

### Memory Tool Constraints
- `/transcripts/` is **read-only** - any modification attempts will raise `PermissionError`
- `str_replace` requires `old_str` to be unique (appears exactly once)
- `str_replace` cannot use empty strings or single newlines
- File operations automatically validate paths to prevent directory traversal

### Multi-threading Configuration
Located in `query_handler_multithreaded.py:259`:
```python
max_workers = 5  # Number of parallel threads
```

### Output Suppression Rules
The system is configured to suppress intermediate output and only show final results. Prompts enforce:
- No process descriptions ("Analyzing files...", "Checking transcripts...")
- Only final output: `"✅ Анализ завершён. Отчёт: /memories/filename.txt"`

## Testing

Test data located in `tests/`:
- `Demo2Pilots DB Test/` - Sample analytics database and queries
- Transcript samples with both correct and corrupted filenames
- Example profiles and progress reports

## File Locations

- **Source code**: Root directory (`.py` files)
- **Prompts**: `prompts/` directory
- **Memory storage**: `memory/memories/` (generated analyses)
- **Transcripts**: `memory/transcripts/` (meeting recordings)
- **Test outputs**: `tests/`

## Common Pitfalls

1. **Meeting ID counting**: IDs are not sequential - always count actual records, not max/min ID
2. **Transcript encoding**: Files use UTF-8, but may have encoding issues (handle with `errors="replace"`)
3. **Thread safety**: Each thread gets its own client instance but shares the same MemoryTool
4. **Context window**: 1M tokens available, but individual responses limited by `max_tokens` parameter
5. **client_task_classification**: Remember this is a classification (1/2/3), not a quality score

## API Usage Notes

All scripts use:
- Extended context beta: `context-1m-2025-08-07`
- Context management beta: `context-management-2025-06-27`
- Tool runner pattern: `client.beta.messages.tool_runner()`
- Russian language for all outputs and prompts
