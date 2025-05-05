#!/bin/bash
# backend/
cd backend || exit 1
source .venv/bin/activate
cd src || exit 1
uvicorn app.main:app --reload