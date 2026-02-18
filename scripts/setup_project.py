import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

FOLDERS = [
    "backend/app/api/routes",
    "backend/app/core",
    "backend/app/db",
    "backend/app/models",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/ai",
    "backend/app/memory",
    "backend/app/data",
    "backend/app/utils",
    "backend/tests",
    "frontend",
]

FILES = {
    "backend/app/main.py": "",
    "backend/app/api/dependencies.py": "",
    "backend/app/db/base.py": "",
    "backend/app/db/session.py": "",
    "backend/app/db/repository.py": "",
    "backend/app/core/config.py": "",
    "backend/app/core/logging.py": "",
    "backend/requirements.txt": "",
    "backend/Dockerfile": "",
    "frontend/Dockerfile": "",
    "docker-compose.yml": "",
    ".env.example": "",
    ".gitignore": "",
    "README.md": "",
}


def create_folders():
    for folder in FOLDERS:
        path = BASE_DIR / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"[✓] Folder ensured: {folder}")


def create_files():
    for file_path, content in FILES.items():
        full_path = BASE_DIR / file_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            print(f"[✓] File created: {file_path}")
        else:
            print(f"[•] File already exists: {file_path}")


def create_init_files():
    for folder in FOLDERS:
        path = BASE_DIR / folder
        init_file = path / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
            print(f"[✓] __init__.py added: {init_file}")


if __name__ == "__main__":
    print("Initializing AI Insights Assistant Project...")
    create_folders()
    create_files()
    create_init_files()
    print("Project structure initialized successfully.")
