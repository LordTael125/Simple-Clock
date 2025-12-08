import PyInstaller.__main__
import os
import sys

# Define the separator for add-data based on OS
# Linux/Mac use ':', Windows uses ';'
separator = ':' if os.name == 'posix' else ';'

print("Building SimpleClock...")

PyInstaller.__main__.run([
    '../main.py',
    '--onefile',
    '--windowed',
    f'--add-data=../ui/clock.ui{separator}ui',
    f'--add-data=../icon.png{separator}.',
    '--name=SimpleClock',
    '--clean',
    '--distpath=../builds/dist',
    '--workpath=../builds/build',
    '--specpath=../builds',
])

print("Build complete. Executable should be in the 'dist' folder.")
