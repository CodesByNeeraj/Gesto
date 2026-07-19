# Gesto

Use gestures to control your laptop

## Build the macOS app

From an activated Python environment on macOS, install the runtime and build
dependencies, then create the branded application bundle:

```bash
python -m pip install -r requirements.txt -r requirements-build.txt
scripts/build-macos-app.sh
open dist/Gesto.app
```

The result is `dist/Gesto.app`. Its Dock icon and display name are Gesto rather
than Python.
