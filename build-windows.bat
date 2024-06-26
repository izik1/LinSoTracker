@REM call activate LinSoTrackerRelease

rmdir /s /q "dist"
rmdir /s /q "_pycache_"
rmdir /s /q "build"
del "LinSoTracker.spec"

pyinstaller --clean --onefile --version-file "properties.rc" --icon "icon.ico"  "LinSoTracker.py"

robocopy "templates" "dist/templates" /E
copy tracker.data dist\tracker.data /Y

ren dist LinSoTracker-Windows
7z a -tzip LinSoTracker-win-x64.zip LinSoTracker-Windows

@REM call conda deactivate