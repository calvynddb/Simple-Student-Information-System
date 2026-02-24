Likely unused imports and suggested actions

Files scanned: core UI and views.

Findings:

- `views/students.py`:
  - Removed conditional imports for `numpy`, `matplotlib`, and `FigureCanvasTkAgg` because the file does not use these libraries. If you rely on charts here, re-add local imports in the functions that need them.

- `dashboard/main.py` and `dashboard.py`:
  - Removed top-level try/except importing matplotlib/numpy. If charts are required in these modules, import them locally where used.

- `numpy` imports:
  - `import numpy as np` appeared in several files but there were no usages of `np` detected (only import lines). I removed the top-level imports where safe.

- `FigureCanvasTkAgg` / `matplotlib` imports:
  - Only `views/programs.py` uses `FigureCanvasTkAgg`/`plt` to render charts; leave those imports in that file.

Recommendations before bundling:

- Run the application and exercise charts to ensure charts still work (they are now only imported where used).
- Run `python -m pip install -r requirements.txt` in your virtualenv before running PyInstaller.
- Search for other absolute paths (I replaced one refresh icon path already).
- Many `messagebox` calls use native dialogs which cannot be themed; consider replacing with `show_custom_dialog` where consistent theming is required.

If you want, I can now:
- Run a safe automated patch that removes other unused imports (based on exact symbol usage), or
- Run the app (in this environment) and perform a smoke test including dialogs and Add modals, or
- Generate a PyInstaller spec file that bundles `assets` and icons explicitly.

Tell me which follow-up you'd like.