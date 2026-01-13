"""
Утилиты для работы с файлами и JSON.
"""
import os
import json
from typing import Dict, Any, Optional
import config


def read_json(file_path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Безопасное чтение JSON файла.
    
    Args:
        file_path: Путь к JSON файлу
        default: Значение по умолчанию, если файл не существует
        
    Returns:
        Словарь с данными из JSON файла или default
        
    Raises:
        json.JSONDecodeError: Если файл содержит некорректный JSON
        IOError: Если не удалось прочитать файл
    """
    default = default if default is not None else {}
    
    if not os.path.isfile(file_path):
        return default
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            # Если файл пустой или содержит не словарь
            if not isinstance(data, dict):
                return default
            return data
    except json.JSONDecodeError:
        raise
    except Exception as e:
        raise IOError(f"Не удалось прочитать файл {file_path}: {e}")


def write_json(file_path: str, data: Dict[str, Any]) -> None:
    """
    Безопасная запись JSON файла.
    
    Args:
        file_path: Путь к JSON файлу
        data: Данные для записи
        
    Raises:
        IOError: Если не удалось записать файл
        OSError: Если не удалось создать директорию
    """
    try:
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=config.JSON_INDENT, 
                     ensure_ascii=config.JSON_ENSURE_ASCII)
    except Exception as e:
        raise IOError(f"Не удалось записать файл {file_path}: {e}")


def write_text_file(file_path: str, content: str) -> None:
    """
    Безопасная запись текстового файла.
    
    Args:
        file_path: Путь к файлу
        content: Содержимое для записи
        
    Raises:
        IOError: Если не удалось записать файл
        OSError: Если не удалось создать директорию
    """
    try:
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        raise IOError(f"Не удалось записать файл {file_path}: {e}")


def ensure_dir(directory: str) -> None:
    """
    Создает директорию, если её не существует.
    
    Args:
        directory: Путь к директории
    """
    os.makedirs(directory, exist_ok=True)
