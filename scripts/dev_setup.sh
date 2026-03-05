#!/bin/bash

echo "================================="
echo "AI Insights Assistant Dev Setup"
echo "================================="

rm insights.db

source ../ai-insights-assistant-venv/bin/activate
echo "Activating virtual environment..."
# Move to backend


echo "Activating virtual environment..."

cd backend || exit
echo "Recreating database..."

echo "Seeding data..."
python3 -m app.data.seed

echo "Starting backend server..."
uvicorn app.main:app --reload

