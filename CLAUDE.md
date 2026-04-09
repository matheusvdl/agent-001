# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn main:app --reload
```

## Architecture

This is a FastAPI-based AI agent API. The entry point is `main.py`, which defines the `app` instance and all routes. Server startup/shutdown logic lives in the `lifespan` context manager.

New routes and agent logic should be added to `main.py` or extracted into separate modules and registered on the `app` instance.
