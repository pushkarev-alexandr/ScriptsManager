"""
Модуль для создания меню Nuke.
"""
from typing import Dict, Any
# nukescripts нужен чтобы некоторые скрипты при exec() явно не импортируют nukescripts,
# поэтому импортирую самостоятельно на всякий случай(а случай был)
import nuke, nukescripts
import config
from script_info_manager import ScriptInfoManager


class MenuBuilder:
    """Класс для построения меню Nuke."""
    
    def __init__(self, script_info_manager: ScriptInfoManager):
        """
        Args:
            script_info_manager: Менеджер информации о скриптах
        """
        self.info_manager = script_info_manager
    
    def write_menu_command(self, file, info: Dict[str, Any], create_menus: bool = False) -> None:
        """
        Записывает команду меню в файл и/или создает меню в Nuke.
        
        Args:
            file: Файловый объект для записи
            info: Информация о скрипте
            create_menus: Создавать ли меню в Nuke немедленно
        """
        if info.get("custom_cmd_checkbox", False):
            custom_command = info.get("custom_command", "")
            file.write(custom_command + "\n")
            if create_menus:
                try:
                    exec(custom_command)
                except Exception as e:
                    nuke.message(f"Не получилось выполнить текущую команду:\n{custom_command}\n\nОшибка:\n{e}")
        else:
            self._write_standard_menu_command(file, info, create_menus)
    
    def _write_standard_menu_command(self, file, info: Dict[str, Any], create_menus: bool) -> None:
        """Записывает стандартную команду меню."""
        menu_path = info.get("menu_path", "")
        command = info.get("command", "")
        icon = info.get("icon", "")
        shortcut = info.get("shortcut", "")
        context = info.get("shortcut_context", "Без контекста")
        index = info.get("index", -1)
        
        context_value = config.SHORTCUT_CONTEXTS.get(context)
        
        if context_value is not None:
            file.write(
                f"nuke.menu('Nuke').addCommand('{menu_path}', '{command}', "
                f"'{shortcut}', icon='{icon}', index={index}, "
                f"shortcutContext={context_value})\n"
            )
            if create_menus:
                nuke.menu("Nuke").addCommand(
                    menu_path, command, shortcut, 
                    icon=icon, index=index, 
                    shortcutContext=context_value
                )
        else:
            file.write(
                f"nuke.menu('Nuke').addCommand('{menu_path}', '{command}', "
                f"'{shortcut}', icon='{icon}', index={index})\n"
            )
            if create_menus:
                nuke.menu("Nuke").addCommand(
                    menu_path, command, shortcut, 
                    icon=icon, index=index
                )
    
    def remove_menu(self, info: Dict[str, Any]) -> None:
        """
        Удаляет меню из Nuke.
        
        Args:
            info: Информация о скрипте
        """
        menu_paths = self._extract_menu_paths(info)
        
        for menu_path in menu_paths:
            try:
                path_parts = menu_path.split("/")
                menu = "/".join(path_parts[:-1])
                
                m = nuke.menu("Nuke").menu(menu)
                if not m:
                    m = nuke.menu("Nuke")
                
                if isinstance(m, nuke.Menu) and m.findItem(path_parts[-1]):
                    m.removeItem(path_parts[-1])
                
                # Удаляем пустое меню, если оно стало MenuItem
                base_menu = nuke.menu("Nuke").findItem(path_parts[0])
                if not isinstance(base_menu, nuke.Menu):
                    nuke.menu("Nuke").removeItem(path_parts[0])
            except Exception:
                pass
    
    def _extract_menu_paths(self, info: Dict[str, Any]) -> list:
        """Извлекает пути меню из информации о скрипте."""
        menu_paths = []
        
        if info.get("custom_cmd_checkbox", False):
            custom_command = info.get("custom_command", "")
            for line in custom_command.split("\n"):
                if line.count(".addCommand(") == 1:
                    try:
                        menu_path = line.split(".addCommand(")[1].split(",")[0].strip("'").strip('"')
                        menu_paths.append(menu_path)
                    except Exception:
                        pass
        else:
            menu_path = info.get("menu_path", "")
            if menu_path:
                menu_paths.append(menu_path)
        
        return menu_paths


def get_in_menu_name(menu_path: str, strip: bool = True) -> str:
    """
    Извлекает имя пункта меню из пути.
    
    Args:
        menu_path: Полный путь в меню
        strip: Удалять ли обратные слеши
        
    Returns:
        Имя пункта меню
    """
    parts = menu_path.split("/")
    if len(parts) > 1 and parts[-2].endswith("\\"):
        part = parts[-2].rstrip("\\") if strip else parts[-2]
        return f"{part}/{parts[-1]}"
    return parts[-1]
