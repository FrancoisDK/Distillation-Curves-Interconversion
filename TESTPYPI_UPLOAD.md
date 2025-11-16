# TestPyPI Upload Instructions

## 📋 Setup (One-time only)

### 1. Create TestPyPI Account
- Visit: https://test.pypi.org/account/register/
- Sign up with email
- Verify your email

### 2. Create API Token
- Log in to https://test.pypi.org/account/
- Click "Add API token" 
- Copy the token (looks like: `pypi-AgEIcHlwaS5vcmc...`)

### 3. Create ~/.pypirc File

**On Windows, create:** `C:\Users\<YourUsername>\.pypirc`

With content:
```ini
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Replace with your TestPyPI token

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Replace with your PyPI token (later)
```

**Alternative: Use command-line token**
```bash
twine upload --repository testpypi --username __token__ --password "pypi-AgEIcHl..." dist/*
```

---

## 🚀 Upload Commands

### Option A: Using ~/.pypirc (recommended)
```bash
cd D:\pyScripts\Distillation_Curve_interconv
twine upload --repository testpypi dist/*
```

### Option B: Using command-line credentials
```bash
twine upload --repository testpypi \
  --username __token__ \
  --password "pypi-AgEIcHlwaS5vcmc..." \
  dist/*
```

### Option C: Using environment variable
```bash
$env:TWINE_PASSWORD = "pypi-AgEIcHlwaS5vcmc..."
twine upload --repository testpypi --username __token__ dist/*
```

---

## ✅ Verification

After upload (wait 1-2 minutes for processing):

1. Visit: https://test.pypi.org/project/distillation-curve-interconv/
2. Verify package appears with version 0.2.0
3. Check README displays correctly
4. Check downloads section shows both .whl and .tar.gz

---

## 🧪 Install from TestPyPI

```bash
# Create test environment
python -m venv test_env
test_env\Scripts\activate

# Install from TestPyPI (note the -i flag)
pip install -i https://test.pypi.org/simple/ distillation-curve-interconv

# Or with dependencies
pip install -i https://test.pypi.org/simple/ distillation-curve-interconv[gui]

# Test it works
python -c "from bp_conversions import Oil; print('✓ Works!')"

# Clean up
deactivate
rmdir /s test_env
```

---

## ⚠️ Troubleshooting

### "Repository not found" error
- Make sure ~/.pypirc exists
- Check [testpypi] section is spelled correctly

### "Unauthorized" error  
- Verify API token is correct
- Token shouldn't be wrapped in quotes in .pypirc

### Package doesn't appear after upload
- Wait 2-3 minutes for PyPI to index
- Try refreshing browser cache
- Check package name: `distillation-curve-interconv` (with hyphens)

### File already exists error
- Can't upload same version twice
- Increment version in pyproject.toml if retesting
- Or use `twine upload --skip-existing dist/*`

---

## 📍 Status After Upload

You should see in terminal:
```
Uploading distillation_curve_interconv-0.2.0.tar.gz ... [OK]
Uploading distillation_curve_interconv-0.2.0-py3-none-any.whl ... [OK]
```

Visit TestPyPI to verify:
```
https://test.pypi.org/project/distillation-curve-interconv/0.2.0/
```
