@echo off
title Code Intelligence Launcher
echo ==========================================
echo 🚀 STARTING CODE INTELLIGENCE ASSISTANT
echo ==========================================

:: 1. Start the Backend in a new window
echo [*] Launching Neural Engine (Backend)...
start "Neural Engine (Backend)" cmd /k "python start_backend.py"

:: 2. Wait for Backend to initialize
echo [!] Waiting for engine to warm up (10 seconds)...
timeout /t 10 /nobreak > nul

:: 3. Start the Frontend in a new window
echo [*] Launching Neural Interface (Frontend)...
cd frontend
start "Neural Interface (Frontend)" cmd /k "npm run dev"

echo ==========================================
echo ✅ SYSTEM IS STARTING UP
echo ==========================================
echo [!] Check the new windows for progress.
echo [!] Once Frontend says "Local: http://localhost:3000", 
echo [!] open your browser and go to that address.
echo ==========================================
pause
