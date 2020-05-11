#!/usr/bin/env bash
echo "setting up dev environment"
pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
