#!/usr/bin/env python3
"""
依存パッケージをインストール
"""

import subprocess
import sys

def install_dependencies():
    """必要なPythonパッケージをインストール"""
    packages = [
        "requests>=2.31.0",
        "feedparser>=6.0.10",
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("\n✅ All dependencies installed!")

if __name__ == "__main__":
    install_dependencies()
