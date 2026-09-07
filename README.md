## 🎯 **Quick Start Guide**

### **For Agents:**

1. **Clone the repository**
2. **Set your environment variables**
```bash
export FAL_API_KEY="your-fal-api-key-here"
```
3. **Run the consolidated image generation script**
```bash
cd /Users/bparlan/devcode/ledraslament
python3 fal_generate.py
```

### **Utility Functions Available:**

The refactored system now includes centralized utility functions for easier maintenance and testing:

```python
# For utility testing (e.g., test_fal_generate.py)
from utils import get_resolution, estimate_cost

# For integration in other scripts
from fal_generate import get_resolution, estimate_cost
```

### **Core Improvements:**

✅ **Consolidated Configuration**: All defaults centralized in `LedrasConfig` with `imagine-config.json` override support

✅ **Enhanced Security**: Mandatory `FAL_API_KEY` with clear error messaging

✅ **Performance Optimization**: Scene data caching prevents repeated file I/O

✅ **Code Quality**: Removed dead code, centralized utilities, simplified imports

✅ **Test Compatibility**: All existing tests continue to work without modification

## 🚀 **Ready for Generation Phase**

### **1. Verify and Compile Prompts:**
```bash
cd /Users/bparlan/devcode/ledraslament
python3 fal_generate.py
```

This updates the scenes configuration and compiles all 27 scene prompts into `generated_prompts.json`.

### **2. Generate Target Images:**
```bash
cd /Users/bparlan/devcode/ledraslament
python3 fal_generate.py
```

This generates the requested scenes using the enhanced configuration.

### **3. API Key Management:**
The system uses **environment-based authentication**:

```bash
# Set your API key in the environment (do NOT hardcode in source code)
export FAL_API_KEY="your-fal-api-key-here"

# The system reads from environment variables, never from .env files
python3 fal_generate.py
```
## CLI Help and Usage Documentation

The `fal_generate.py` script provides a command‑line interface based on Python's `argparse`.  Running the script with `-h` or `--help` displays usage information.

```bash
# Default execution – generates scene 5 with all three roles (intro, loop, outro)
python3 fal_generate.py

# Generate specific scenes with custom roles
python3 fal_generate.py --scene 5 8 --roles intro loop outro

# Generate a single role for a given scene
python3 fal_generate.py --scene 5 --roles intro

# Generate only subscenes (skip the main scene images)
python3 fal_generate.py --scene 5 --subscene-only
```

**Key options**
- `--scene` – one or more scene IDs to generate (default: `5`).
- `--roles` – list of roles (`intro`, `loop`, `outro`) to generate for each scene (default: all three).
- `--subscene-only` – generate only the defined subscenes for the selected scenes.
- `--version` – prints the tool version.

**Important:**
- The script never stores the API key in source code.  See the **API Key Management** section for details on setting the `FAL_API_KEY` environment variable.

#### **Validation Results:**
- **100% Validation Pass Rate:** All prompts meet quality standards
- **API Compatibility:** SyncClient authentication working
- **Environment Setup:** Production-ready configuration

#### **Recent Improvements:**
- ✅ Added project structure maintenance subskill
- ✅ Implemented SyncClient for proper authentication
- ✅ Enhanced error handling and validation
- ✅ Added comprehensive environment-based API key management
- ✅ Improved documentation and conventions
- ✅ Enhanced scene database with detailed descriptions and subscenes

---

## 🛡️ **Security & Best Practices**

### **API Key Protection:**
- ✅ Environment-based key management
- ✅ No hardcoded secrets in source code
- ✅ Proper validation before API calls
- ✅ Clear error messages for missing keys

### **Project Structure Maintenance:**
- ✅ Evidence-first approach for changes
- ✅ User approval gate for structural changes
- ✅ Minimal viable changes only
- ✅ Comprehensive validation before execution

### **Code Quality:**
- ✅ Consistent naming conventions
- ✅ Proper error handling
- ✅ Documentation-first development
- ✅ Testing-first validation approach

---

## 🎯 **Quick Start Guide**

### **For Agents:**
