import os
import shutil
import urllib.request
import stat
import subprocess

APP_NAME = "SimpleClock"
EXECUTABLE_NAME = "SimpleClock"
# Paths relative to scripts/ directory
BUILDS_DIR = os.path.join("..", "builds")
DIST_PATH = os.path.join(BUILDS_DIR, "dist", EXECUTABLE_NAME)
APP_IMAGE_DIR = os.path.join(BUILDS_DIR, "AppImage")
APP_DIR = os.path.join(APP_IMAGE_DIR, f"{APP_NAME}.AppDir")

def create_structure():
    print(f"Creating {APP_DIR} structure...")
    if os.path.exists(APP_DIR):
        shutil.rmtree(APP_DIR)
    
    os.makedirs(os.path.join(APP_DIR, "usr", "bin"))
    os.makedirs(os.path.join(APP_DIR, "usr", "share", "applications"))
    os.makedirs(os.path.join(APP_DIR, "usr", "share", "icons", "hicolor", "256x256", "apps"))

def copy_executable():
    print("Copying executable...")
    if not os.path.exists(DIST_PATH):
        print(f"Error: {DIST_PATH} not found. Please run build.py first.")
        exit(1)
    
    dest = os.path.join(APP_DIR, "usr", "bin", EXECUTABLE_NAME)
    shutil.copy2(DIST_PATH, dest)

def create_desktop_file():
    print("Creating .desktop file...")
    content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Exec={EXECUTABLE_NAME}
Icon=simpleclock
Categories=Utility;Clock;
Terminal=false
"""
    desktop_path = os.path.join(APP_DIR, "usr", "share", "applications", f"{APP_NAME}.desktop")
    with open(desktop_path, "w") as f:
        f.write(content)
    
    # Symlink at root
    # Relative symlink from AppDir root to usr/share/applications/...
    # Target: usr/share/applications/SimpleClock.desktop
    # Link name: SimpleClock.desktop
    link_path = os.path.join(APP_DIR, f"{APP_NAME}.desktop")
    if os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(os.path.join("usr", "share", "applications", f"{APP_NAME}.desktop"), link_path)

def create_icon():
    print("Creating icon...")
    # 1x1 red pixel PNG
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'
    
    icon_path = os.path.join(APP_DIR, "usr", "share", "icons", "hicolor", "256x256", "apps", "simpleclock.png")
    with open(icon_path, "wb") as f:
        f.write(png_data)
        
    # Symlink at root
    link_path = os.path.join(APP_DIR, "simpleclock.png")
    if os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(os.path.join("usr", "share", "icons", "hicolor", "256x256", "apps", "simpleclock.png"), link_path)

def create_apprun():
    print("Creating AppRun...")
    # Symlink to usr/bin/SimpleClock
    link_path = os.path.join(APP_DIR, "AppRun")
    if os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(os.path.join("usr", "bin", EXECUTABLE_NAME), link_path)

def download_appimagetool():
    url = "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    filename = "appimagetool-x86_64.AppImage"
    
    # Check in scripts dir (current dir)
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        os.chmod(filename, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    return os.path.abspath(filename)

def build_appimage(tool_path):
    print("Building AppImage...")
    env = os.environ.copy()
    env["ARCH"] = "x86_64"
    
    # Output file path
    # appimagetool outputs to current directory by default, or we can specify
    # We want it in builds/AppImage/
    
    # Run appimagetool on the AppDir
    # It will create the AppImage in the current working directory (scripts/)
    # We should move it after creation or run it from the destination
    
    subprocess.run([tool_path, APP_DIR], env=env, check=True)
    
    # Move generated AppImage to builds/AppImage/
    # The name is usually SimpleClock-x86_64.AppImage
    generated_name = f"{APP_NAME}-x86_64.AppImage"
    if os.path.exists(generated_name):
        shutil.move(generated_name, os.path.join(APP_IMAGE_DIR, generated_name))

def main():
    # Ensure builds/AppImage exists
    if not os.path.exists(APP_IMAGE_DIR):
        os.makedirs(APP_IMAGE_DIR)

    create_structure()
    copy_executable()
    create_desktop_file()
    create_icon()
    create_apprun()
    
    tool_path = download_appimagetool()
    build_appimage(tool_path)
    print(f"Success! {APP_NAME}-x86_64.AppImage created in builds/AppImage/")

if __name__ == "__main__":
    main()
