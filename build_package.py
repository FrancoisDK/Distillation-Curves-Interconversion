#!/usr/bin/env python
"""
Build and package script for PyPI distribution
Run: python build_package.py
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    print(f"✅ Success: {description}")
    return True

def main():
    """Build and package the project"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     Distillation Curve Interconversion - Build Package         ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 12):
        print(f"❌ Python 3.12+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Step 1: Install build tools
    if not run_command(
        "pip install --upgrade build twine",
        "Installing build tools"
    ):
        return False
    
    # Step 2: Run tests (optional but recommended)
    print("\n📋 Optional: Run tests before packaging?")
    print("   If tests fail, packaging will continue anyway.")
    response = input("   Run tests? [y/N]: ").strip().lower()
    
    if response in ['y', 'yes']:
        run_command(
            "pip install -e '.[dev]' && pytest tests/ -v",
            "Running tests"
        )
    
    # Step 3: Clean old builds
    print(f"\n🧹 Cleaning old builds...")
    dist_dir = Path("dist")
    build_dir = Path("build")
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
        print("   ✓ Removed dist/")
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
        print("   ✓ Removed build/")
    
    # Step 4: Build distribution
    if not run_command(
        "python -m build",
        "Building wheel and source distributions"
    ):
        return False
    
    # Step 5: Check package
    if not run_command(
        "twine check dist/*",
        "Validating package metadata"
    ):
        return False
    
    # Step 6: Show results
    print(f"\n{'='*60}")
    print("📦 Build Complete!")
    print(f"{'='*60}")
    
    dist_files = list(Path("dist").glob("*"))
    for f in dist_files:
        size_mb = f.stat().st_size / (1024*1024)
        print(f"  ✓ {f.name} ({size_mb:.1f} MB)")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Local test install: pip install dist/distillation_curve_interconv-*.whl")
    print(f"   2. Test in new venv: pip install dist/distillation*.tar.gz")
    print(f"   3. Upload to TestPyPI: twine upload --repository testpypi dist/*")
    print(f"   4. Upload to PyPI: twine upload dist/*")
    
    print(f"\n💡 For TestPyPI (test first):")
    print(f"   1. Create account: https://test.pypi.org/account/register/")
    print(f"   2. Create API token in account settings")
    print(f"   3. Create ~/.pypirc:")
    print(f"""
    [distutils]
    index-servers =
        testpypi
        pypi

    [testpypi]
    repository = https://test.pypi.org/legacy/
    username = __token__
    password = pypi-...  # Your TestPyPI token

    [pypi]
    username = __token__
    password = pypi-...  # Your PyPI token
    """)
    print(f"   4. Upload: twine upload --repository testpypi dist/*")
    print(f"   5. Install: pip install -i https://test.pypi.org/simple/ distillation-curve-interconv")
    print(f"   6. If all good, upload to PyPI: twine upload dist/*")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
