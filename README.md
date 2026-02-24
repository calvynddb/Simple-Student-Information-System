<p align="center">
  <img src="assets/banner.png" alt="nexo banner" width="600"/>
</p>

<h1 align="center">nexo</h1>

<p align="center">
  <b>A Simple Student Information System</b><br/>
  Built with Python &amp; CustomTkinter
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.13-blue?logo=python&logoColor=white" alt="Python 3.13"/>
  <img src="https://img.shields.io/badge/UI-CustomTkinter-purple" alt="CustomTkinter"/>
  <img src="https://img.shields.io/badge/data-CSV-green" alt="CSV Storage"/>
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="MIT License"/>
</p>

---

## Screenshots

| Login | Dashboard | Student Profile |
|:---:|:---:|:---:|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) | ![Profile](screenshots/profile.png) |

| Programs View | Colleges View | Settings |
|:---:|:---:|:---:|
| ![Programs](screenshots/programs.png) | ![Colleges](screenshots/colleges.png) | ![Settings](screenshots/settings.png) |

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Default Credentials](#default-credentials)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Data Model](#data-model)
- [Building the Executable](#building-the-executable)

---

## Overview

nexo is a desktop student information system built with Python and CustomTkinter. It manages students, academic programs, and colleges through a dark-themed GUI backed by CSV flat files — no database required.

**Core features:**

- **CRUD** — create, read, update, and delete students, programs, and colleges. Forms open as themed modal popups with field validation; deletes require confirmation.
- **Real-time search** — filters the active table as you type, matching across all visible fields.
- **Sortable columns** — click any header to toggle ascending/descending order, with a numeric-aware sort for the year column.
- **Pagination** — prev/next and numbered page buttons with a go-to-page input; page size adjusts dynamically to the window height.
- **Student profiles** — click any row to open a detail popup with full info and quick edit/delete actions.
- **Charts** — donut chart (matplotlib) showing program distribution by college, plus a top enrolled programs sidebar.
- **Auth & guest mode** — admin login with SHA-256 hashed passwords. Guest mode grants full read-only access without logging in. New admins can be registered from the login screen.
- **CSV import** — bulk-import records from external CSV files with per-row validation, error reporting, and duplicate detection.
- **Portable executable** — packages into a single `.exe` via PyInstaller; CSV data files are seeded on first launch.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.13+ |
| UI Framework | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Charts | Matplotlib + NumPy |
| Image Loading | Pillow (PIL) |
| Data Storage | CSV (flat file) |
| Packaging | PyInstaller |

---

## Getting Started

### Prerequisites

- Python **3.13** or later
- pip

> Python 3.14 has a known NumPy DLL incompatibility with PyInstaller — use 3.13 if you plan to build an executable.

### Installation

```bash
# clone the repository
git clone https://github.com/calvynddb/Simple-Student-Information-System.git
cd Simple-Student-Information-System

# (recommended) create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # windows
# source .venv/bin/activate  # mac/linux

# install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

The app opens at **1400 × 900** in dark mode. CSV data files are created automatically on first launch.

---

## Default Credentials

| Username | Password |
|---|---|
| `admin` | `admin` |

> You can register additional administrators from the login screen.

---

## Project Structure

```
nexo/
├── main.py                          # Entry point — App class, frame management, custom dialogs
├── config.py                        # Colors, fonts, file paths, ThemeManager, path helpers
├── requirements.txt                 # Python dependencies
├── build_exe.bat                    # PyInstaller build script
│
├── assets/
│   ├── Main Logo.png                # App logo
│   └── icons/                       # 58 PNG icons (18/22/28/36 px sizes)
│
├── backend/                         # Data layer (no UI dependencies)
│   ├── __init__.py                  # Public API — init_files, load_csv, save_csv, create_backups
│   ├── storage.py                   # CSV file I/O (init, load, save, backup, seed copy)
│   ├── validators.py                # Field-level validation for all entities
│   ├── crud/
│   │   ├── students.py              # StudentCRUD — create / read / update / delete / list
│   │   ├── programs.py              # ProgramCRUD
│   │   └── colleges.py              # CollegeCRUD
│   ├── search/
│   │   ├── students.py              # StudentSearch — by_id, by_name, by_field, by_any_field
│   │   ├── programs.py              # ProgramSearch
│   │   └── colleges.py              # CollegeSearch
│   └── sort/
│       ├── students.py              # StudentSort — by_id, by_name, by_year, by_program, etc.
│       ├── programs.py              # ProgramSort
│       └── colleges.py              # CollegeSort
│
├── frontend_ui/                     # Presentation layer
│   ├── auth/
│   │   └── login.py                 # LoginFrame — sign in, register, guest access
│   ├── dashboard/
│   │   └── main.py                  # DashboardFrame — topbar, nav tabs, settings modal
│   ├── views/
│   │   ├── students.py              # StudentsView — table, profile, add/edit/import
│   │   ├── programs.py              # ProgramsView — table, donut chart, top enrolled sidebar
│   │   └── colleges.py              # CollegesView — table, add/edit/import
│   └── ui/
│       ├── cards.py                 # DepthCard, StatCard components
│       ├── inputs.py                # SearchableComboBox, StyledComboBox, SmartSearchEntry
│       └── utils.py                 # Icon/logo loader, Treeview styling, animations
│
├── students.csv                     # Student records
├── programs.csv                     # 59 pre-seeded programs
├── colleges.csv                     # 7 pre-seeded colleges
└── users.csv                        # Admin credentials (username + SHA-256 hash)
```

---

## Architecture

The project follows a **layered architecture** with clear separation between data and presentation:

```
┌──────────────────────────────────────────────┐
│                  main.py                     │
│          App shell, frame switching          │
├──────────────┬───────────────────────────────┤
│  frontend_ui │          config.py            │
│  ┌─────────┐ │   Colors, fonts, paths,       │
│  │  auth/  │ │   ThemeManager                │
│  │dashboard│ │                               │
│  │ views/  │ │                               │
│  │  ui/    │ │                               │
│  └────┬────┘ │                               │
│       │      │                               │
├───────┴──────┴───────────────────────────────┤
│                 backend/                     │
│   storage ← crud / search / sort            │
│   validators                                │
├──────────────────────────────────────────────┤
│              CSV flat files                  │
│   students.csv  programs.csv  colleges.csv   │
└──────────────────────────────────────────────┘
```

**Key design decisions:**

1. **Backend / Frontend split** — The `backend/` package has zero UI imports; it only deals with CSV data, validation, and business logic.
2. **CRUD, Search, Sort classes** — Each entity (Student, Program, College) has its own dedicated class for each operation type.
3. **Centralized config** — All colors, fonts, file paths, and theme state live in `config.py`.
4. **Custom dialog system** — A single `show_custom_dialog()` replaces all native message boxes with themed modal windows.
5. **Path helpers** — `resource_path()` and `data_path()` enable seamless PyInstaller bundling.

---

## Data Model

### Students

| Field | Description |
|---|---|
| `id` | Unique student ID (e.g. `2023-0001`) — no letters allowed |
| `firstname` | First name — alphabetic only |
| `lastname` | Last name — alphabetic only |
| `gender` | Male / Female / Other |
| `year` | Year level (numeric) |
| `program` | Program code (foreign key to Programs) |

### Programs

| Field | Description |
|---|---|
| `code` | Unique program code (e.g. `BSCS`) |
| `name` | Full program name — no digits allowed |
| `college` | College code (foreign key to Colleges) |

### Colleges

| Field | Description |
|---|---|
| `code` | Unique college code (e.g. `CCS`) |
| `name` | Full college name — no digits allowed |

**Relationships:** Student → Program → College (referential integrity enforced on delete).

---

## Building the Executable

A single-file `.exe` can be built with PyInstaller:

```bash
# Using the build script
.\build_exe.bat

# Or manually
python -m PyInstaller --noconfirm --onefile --windowed ^
    --add-data "assets;assets" ^
    --add-data "config.py;." ^
    --add-data "students.csv;." --add-data "programs.csv;." ^
    --add-data "colleges.csv;." --add-data "users.csv;." ^
    --add-data "backend;backend" --add-data "frontend_ui;frontend_ui" ^
    --hidden-import PIL --hidden-import matplotlib ^
    --hidden-import numpy --hidden-import customtkinter ^
    --collect-all customtkinter --exclude-module PyQt5 ^
    --name nexo main.py
```

The output `dist/nexo.exe` (~38 MB) is fully portable. On first run it seeds CSV data files next to itself.

---

<p align="center">
  Made with ❤️ using Python and CustomTkinter
</p>
