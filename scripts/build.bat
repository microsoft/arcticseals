@echo off
@rem This script ensures that dependent packages are installed, and any build steps (if applicable) are performed.
@rem Assumes certain prerequisites are installed as described in the root README.md. Please add to this as needed.

cd %~dp0/../src/parse-labels
npm install
