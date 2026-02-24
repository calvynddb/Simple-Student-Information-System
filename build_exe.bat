@echo off
REM Build a single-file, windowed executable using PyInstaller
REM Includes all assets, backend, frontend_ui packages, config, and CSV data files.

pyinstaller --noconfirm --onefile --windowed ^
    --add-data "assets;assets" ^
    --add-data "config.py;." ^
    --add-data "students.csv;." ^
    --add-data "programs.csv;." ^
    --add-data "colleges.csv;." ^
    --add-data "users.csv;." ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "matplotlib" ^
    --hidden-import "matplotlib.backends.backend_tkagg" ^
    --hidden-import "numpy" ^
    --hidden-import "customtkinter" ^
    --name nexo ^
    main.py

echo.
echo Build completed. Check the "dist" directory for "nexo.exe".
pause
