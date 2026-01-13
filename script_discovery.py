"""
Модуль для поиска и сканирования скриптов.
"""
import os
from typing import Dict
import nuke
import config


def discover_scripts(add_to_plugin_path: bool = False) -> Dict[str, str]:
    """
    Находит все Python скрипты в директории scripts.
    
    Args:
        add_to_plugin_path: Если True, добавляет директории в Nuke pluginPath
        
    Returns:
        Словарь {имя_скрипта: путь_в_меню}
    """
    scripts = {}
    
    if not os.path.isdir(config.SCRIPTS_DIR):
        return scripts
    
    for root, dirs, files in os.walk(config.SCRIPTS_DIR):
        # Пропускаем исключенные директории
        dirs[:] = [d for d in dirs if d not in config.EXCLUDED_DIRS]
        
        for file in files:
            if file.endswith(".py"):
                # Путь в меню - относительный путь от scripts_dir
                menu_path = root[len(config.SCRIPTS_DIR) + 1:].replace("\\", "/")
                script_name = os.path.splitext(file)[0]
                scripts[script_name] = menu_path
        
        if add_to_plugin_path:
            normalized_path = root.replace("\\", "/")
            nuke.pluginAddPath(normalized_path)
    
    return scripts


def add_scripts_folder_to_plugin_path() -> None:
    """
    Добавляет все папки внутри папки scripts в pluginPath.
    """
    discover_scripts(add_to_plugin_path=True)
