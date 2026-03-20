@echo off
REM MIA - Medical Image Analysis System
REM Quick run script

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                    MIA - MEDICAL IMAGE ANALYSIS SYSTEM                       ║
echo ║                    Powered by Gemini 2.5 Flash ^& Groq                        ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Activate virtual environment and run
.miavenv\Scripts\python.exe miaapp.py

pause
