"""
Менеджер для работы с пользовательскими данными.
"""
import os
from typing import Dict, Optional
import config
from file_utils import read_json, write_json, write_text_file, ensure_dir
from script_info_manager import ScriptInfoManager


class UserDataManager:
    """Класс для управления пользовательскими данными."""
    
    def __init__(self, username: Optional[str] = None):
        """
        Args:
            username: Имя пользователя (по умолчанию текущий)
        """
        self.username = username or config.USERNAME
        self.user_folder = f"{config.USERS_DIR}/{self.username}"
        self.data_file = f"{self.user_folder}/data.json"
        self.menu_file = f"{self.user_folder}/menu.py"
    
    def get_user_data(self) -> Dict[str, bool]:
        """
        Получает данные пользователя о включенных/выключенных скриптах.
        
        Returns:
            Словарь {имя_скрипта: включен_ли}
        """
        return read_json(self.data_file, default={})
    
    def save_user_data(self, data: Dict[str, bool]) -> None:
        """
        Сохраняет данные пользователя.
        
        Args:
            data: Словарь {имя_скрипта: включен_ли}
        """
        ensure_dir(self.user_folder)
        write_json(self.data_file, data)
    
    def get_script_state(self, script_name: str) -> bool:
        """
        Получает состояние скрипта для пользователя.
        
        Args:
            script_name: Имя скрипта
            
        Returns:
            True если включен, False иначе.
            Если у пользователя нет информации о скрипте, возвращается
            значение по умолчанию из scripts_info.json.
            Если скрипта нет в scripts_info.json, возвращается False.
        """
        user_data = self.get_user_data()
        if script_name in user_data:
            return user_data[script_name]
        
        # Если у пользователя нет информации, берем default из scripts_info.json
        script_info_manager = ScriptInfoManager()
        return script_info_manager.get_default_state(script_name)
    
    def set_script_state(self, script_name: str, enabled: bool) -> None:
        """
        Устанавливает состояние скрипта для пользователя.
        
        Args:
            script_name: Имя скрипта
            enabled: Включен ли скрипт
        """
        data = self.get_user_data()
        data[script_name] = enabled
        self.save_user_data(data)
    
    def ensure_user_folder(self) -> None:
        """Создает папку пользователя, если её нет."""
        ensure_dir(self.user_folder)
    
    def menu_file_exists(self) -> bool:
        """Проверяет существование файла меню пользователя."""
        return os.path.isfile(self.menu_file)
    
    def data_file_exists(self) -> bool:
        """Проверяет существование файла данных пользователя."""
        return os.path.isfile(self.data_file)
    
    def write_menu_file(self, content: str) -> None:
        """
        Записывает содержимое в файл меню пользователя.
        
        Args:
            content: Содержимое для записи
        """
        write_text_file(self.menu_file, content)
