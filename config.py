"""
Модуль конфигурации ScriptsManager.
Содержит все константы и пути, используемые в проекте.
"""
import os
import getpass

# Базовые пути
CURRENT_DIR = os.path.dirname(__file__).replace("\\", "/")
SCRIPTS_DIR = f"{os.path.dirname(CURRENT_DIR)}/scripts"
USERS_DIR = f"{CURRENT_DIR}/users"

# Файлы
INFO_FILE = f"{CURRENT_DIR}/scripts_info.json"

# Пользовательские настройки
USERNAME = getpass.getuser()
USER_FOLDER = f"{USERS_DIR}/{USERNAME}"
USER_DATA_FILE = f"{USER_FOLDER}/data.json"
USER_MENU_FILE = f"{USER_FOLDER}/menu.py"

# Пользователи с правами администратора
ADMIN_USERS = ["apushkarev", "pushk", "kzolototrubov"]
ADMIN_USERS = []

# Контексты горячих клавиш
SHORTCUT_CONTEXTS = {
    "Без контекста": None,
    "Window": 0,
    "Application": 1,
    "DAG": 2
}

SHORTCUT_CONTEXT_LABELS = list(SHORTCUT_CONTEXTS.keys())

# Исключаемые папки при сканировании
EXCLUDED_DIRS = ["__pycache__"]

# Формат JSON для сохранения
JSON_INDENT = 4
JSON_ENSURE_ASCII = False
