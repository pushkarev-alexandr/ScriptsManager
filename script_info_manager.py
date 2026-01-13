"""
Менеджер для работы с информацией о скриптах.
"""
import os
from typing import Dict, Any, Optional
import config
from file_utils import read_json, write_json


class ScriptInfoManager:
    """Класс для управления информацией о скриптах."""
    
    def __init__(self):
        self.info_file = config.INFO_FILE
    
    def get_scripts_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Получает информацию о всех скриптах.
        
        Returns:
            Словарь {имя_скрипта: {параметры}}
        """
        return read_json(self.info_file, default={})
    
    def save_scripts_info(self, info: Dict[str, Dict[str, Any]]) -> None:
        """
        Сохраняет информацию о скриптах.
        
        Args:
            info: Словарь с информацией о скриптах
        """
        write_json(self.info_file, info)
    
    def get_script_info(self, script_name: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о конкретном скрипте.
        
        Args:
            script_name: Имя скрипта
            
        Returns:
            Словарь с информацией о скрипте или None
        """
        info = self.get_scripts_info()
        return info.get(script_name)
    
    def update_script_info(self, script_name: str, script_info: Dict[str, Any]) -> None:
        """
        Обновляет информацию о скрипте.
        
        Args:
            script_name: Имя скрипта
            script_info: Словарь с информацией о скрипте
        """
        info = self.get_scripts_info()
        info[script_name] = script_info
        self.save_scripts_info(info)
    
    def remove_script_info(self, script_name: str) -> None:
        """
        Удаляет информацию о скрипте.
        
        Args:
            script_name: Имя скрипта
        """
        info = self.get_scripts_info()
        if script_name in info:
            del info[script_name]
            self.save_scripts_info(info)
    
    def get_default_state(self, script_name: str) -> bool:
        """
        Получает дефолтное состояние скрипта.
        
        Args:
            script_name: Имя скрипта
            
        Returns:
            True если включен по умолчанию, False иначе
        """
        script_info = self.get_script_info(script_name)
        if script_info:
            return script_info.get("default", False)
        return False
    
    def ensure_info_file(self) -> None:
        """Создает файл информации, если его нет."""
        if not os.path.isfile(self.info_file):
            self.save_scripts_info({})
