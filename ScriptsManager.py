"""
ScriptsManager - система управления скриптами для Nuke.
Использует модульную архитектуру и панели на PySide.
"""
import os
import getpass
import nuke
from typing import Optional
from io import StringIO

# Импорты новых модулей
from script_discovery import discover_scripts
from script_info_manager import ScriptInfoManager
from user_data_manager import UserDataManager
from menu_builder import MenuBuilder
from panels.scripts_manager_panel import ScriptsManagerPanel
from panels.edit_script_panel import EditScriptPanel
import config


def scripts_manager():
    """Главное меню для включения/выключения плагинов"""
    try:
        info_manager = ScriptInfoManager()
        user_manager = UserDataManager()
        menu_builder = MenuBuilder(info_manager)
        
        # Проверка наличия файла информации
        if not os.path.isfile(info_manager.info_file):
            nuke.message("Нужен файл scripts_info.json")
            return
        
        # Получение данных
        scripts_info = info_manager.get_scripts_info()
        if not scripts_info:
            nuke.message("Ошибка чтения файла scripts_info.json")
            return
        
        scripts = discover_scripts(add_to_plugin_path=True)
        if not scripts:
            nuke.message("Не нашел ни одного скрипта в папке scripts")
            return
        
        user_data = user_manager.get_user_data()
        
        # Создание и показ панели
        result = ScriptsManagerPanel.show_dialog(scripts, scripts_info, user_data)
        if result is None:
            return
        
        # Сохранение данных
        user_manager.ensure_user_folder()
        
        # Собираем содержимое menu.py
        menu_content_lines = []
        for script_name, enabled in result.items():
            script_info = scripts_info.get(script_name)
            if script_info:
                if enabled:
                    # Записываем команду в menu.py используя StringIO для временного хранения
                    temp_file = StringIO()
                    menu_builder.write_menu_command(temp_file, script_info, create_menus=True)
                    menu_content_lines.append(temp_file.getvalue())
                    temp_file.close()
                else:
                    # Удаляем меню из Nuke
                    menu_builder.remove_menu(script_info)
        
        # Записываем menu.py файл
        menu_content = "".join(menu_content_lines)
        user_manager.write_menu_file(menu_content)
        
        # Сохраняем данные пользователя
        user_manager.save_user_data(result)
        
        nuke.message("Скрипты успешно изменены!\n(возможно потребуется перезагрузить Nuke)")
        
    except (IOError, ValueError) as e:
        nuke.message(f"Ошибка работы с файлами: {e}")
    except Exception as e:
        nuke.message(f"Неожиданная ошибка: {e}")


def edit_script_info():
    """Добавляет/изменяет информацию о скрипте в файле scripts_info.json."""
    try:
        info_manager = ScriptInfoManager()
        
        scripts = discover_scripts()
        if not scripts:
            nuke.message("Не нашел ни одного скрипта в папке scripts")
            return
        
        info_manager.ensure_info_file()
        scripts_info = info_manager.get_scripts_info()
        
        # Показываем панель редактирования
        result = EditScriptPanel.show_dialog(scripts, scripts_info)
        if result is None:
            return
        
        script_name, script_info = result
        info_manager.update_script_info(script_name, script_info)
        update_users_menu()
        
    except (IOError, ValueError) as e:
        nuke.message(f"Ошибка работы с файлами: {e}")
    except Exception as e:
        nuke.message(f"Неожиданная ошибка: {e}")


def remove_script_info():
    """
    Удаляет запись о скрипте в файле scripts_info.json.
    При этом у пользователей этот скрипт не удалится, но он больше не появится
    в списке выбора Scripts Manager.
    """
    try:
        info_manager = ScriptInfoManager()
        
        if not os.path.isfile(info_manager.info_file):
            nuke.message("Нужен файл scripts_info.json")
            return
        
        scripts_info = info_manager.get_scripts_info()
        if not scripts_info:
            nuke.message("Нет информации о скриптах для удаления")
            return
        
        # Создаем простой диалог выбора скрипта
        script_names = sorted(list(scripts_info.keys()))
        p = nuke.Panel("Remove Script")
        p.addEnumerationPulldown("Script", " ".join(script_names))
        
        if p.show():
            script_name = p.value("Script")
            info_manager.remove_script_info(script_name)
            update_users_menu()
            
    except Exception as e:
        nuke.message(f"Ошибка: {e}")


def set_script_state_for_all_users_ui():
    """Окно для установки состояния скрипта для всех пользователей"""
    try:
        info_manager = ScriptInfoManager()
        
        if not os.path.isfile(info_manager.info_file):
            nuke.message("Нужен файл scripts_info.json")
            return
        
        scripts_info = info_manager.get_scripts_info()
        if not scripts_info:
            nuke.message("Нет информации о скриптах")
            return
        
        script_names = sorted(list(scripts_info.keys()))
        p = nuke.Panel("Set Script State For All Users")
        p.addEnumerationPulldown("Script", " ".join(script_names))
        p.addEnumerationPulldown("State", "Enable Disable")
        
        if p.show():
            script_name = p.value("Script")
            state = p.value("State") == "Enable"
            set_script_state_for_all_users(script_name, state)
            nuke.message("Successfully set!")
            
    except Exception as e:
        nuke.message(f"Ошибка: {e}")


def create_user_default_settings(user_manager: Optional[UserDataManager] = None):
    """
    При загрузке Nuke создает для пользователя дефолтные настройки, если у него их еще нет.
    По умолчанию функция выполняется для текущего пользователя, но можно передать
    user_manager для кастомного пользователя.
    """
    try:
        info_manager = ScriptInfoManager()
        user_manager = user_manager or UserDataManager()
        menu_builder = MenuBuilder(info_manager)
        
        # Если настройки уже есть, ничего не делаем
        if user_manager.data_file_exists() and user_manager.menu_file_exists():
            return
        
        scripts = discover_scripts()
        if not scripts:
            return
        
        if not os.path.isfile(info_manager.info_file):
            return
        
        scripts_info = info_manager.get_scripts_info()
        user_manager.ensure_user_folder()
        
        # Собираем данные и содержимое menu.py
        data = {}
        menu_content_lines = []
        
        for script_name in scripts:
            script_info = scripts_info.get(script_name)
            if script_info is None:
                continue
            
            default_enabled = script_info.get("default", False)
            data[script_name] = default_enabled
            
            if default_enabled:
                temp_file = StringIO()
                menu_builder.write_menu_command(temp_file, script_info, create_menus=False)
                menu_content_lines.append(temp_file.getvalue())
                temp_file.close()
        
        # Сохраняем файлы
        menu_content = "".join(menu_content_lines)
        user_manager.write_menu_file(menu_content)
        user_manager.save_user_data(data)
        
    except Exception:
        # Молча игнорируем ошибки при создании дефолтных настроек
        pass


def update_users_menu():
    """
    Для всех пользователей в папке users заново создает menu.py.
    Создание происходит на основе включенных скриптов в userDataFile и новой
    информации из scripts_info.json.
    """
    try:
        info_manager = ScriptInfoManager()
        menu_builder = MenuBuilder(info_manager)
        
        scripts = discover_scripts()
        if not scripts:
            return
        
        if not os.path.isfile(info_manager.info_file):
            return
        
        scripts_info = info_manager.get_scripts_info()
        users_dir = config.USERS_DIR
        
        if not os.path.isdir(users_dir):
            return
        
        for user in os.listdir(users_dir):
            user_folder = os.path.join(users_dir, user)
            if not os.path.isdir(user_folder):
                continue
            
            user_manager = UserDataManager(username=user)
            
            if user_manager.data_file_exists() and user_manager.menu_file_exists():
                # Обновляем существующие настройки
                user_data = user_manager.get_user_data()
                new_data = {}
                menu_content_lines = []
                
                for script_name in scripts:
                    script_info = scripts_info.get(script_name)
                    if script_info is None:
                        continue
                    
                    # Определяем состояние скрипта
                    enabled = user_data.get(script_name)
                    if enabled is None:
                        enabled = script_info.get("default", False)
                    
                    new_data[script_name] = enabled
                    
                    if enabled:
                        temp_file = StringIO()
                        menu_builder.write_menu_command(temp_file, script_info, create_menus=False)
                        menu_content_lines.append(temp_file.getvalue())
                        temp_file.close()
                
                # Сохраняем обновленные файлы
                menu_content = "".join(menu_content_lines)
                user_manager.write_menu_file(menu_content)
                user_manager.save_user_data(new_data)
            else:
                # Создаем дефолтные настройки
                create_user_default_settings(user_manager)
        
        nuke.message("Successfully updated!")
        
    except Exception as e:
        nuke.message(f"Ошибка обновления меню: {e}")


def add_scripts_folder_to_plugin_path():
    """
    Добавляет все папки внутри папки scripts в pluginPath для доступа к ним.
    """
    from script_discovery import add_scripts_folder_to_plugin_path as _add_path
    _add_path()


def create_menu():
    """
    Создает меню для управления скриптами.
    Для обычных пользователей это просто включение и выключение скриптов.
    Для избранных пользователей из списка ADMIN_USERS еще и меню
    для управления информацией о скриптах и удаления информации о скриптах.
    """
    current_user = getpass.getuser()
    
    if current_user in config.ADMIN_USERS:
        nuke.menu("Nuke").addCommand(
            "Edit/Scripts Manager/Scripts Manager",
            "ScriptsManager.scripts_manager()"
        )
        nuke.menu("Nuke").addCommand(
            "Edit/Scripts Manager/Edit Scripts Info",
            "ScriptsManager.edit_script_info()"
        )
        nuke.menu("Nuke").addCommand(
            "Edit/Scripts Manager/Remove Script",
            "ScriptsManager.remove_script_info()"
        )
        nuke.menu("Nuke").addCommand(
            "Edit/Scripts Manager/Set Script State For All Users",
            "ScriptsManager.set_script_state_for_all_users_ui()"
        )
        nuke.menu("Nuke").addCommand(
            "Edit/Scripts Manager/Update Users Menus",
            "ScriptsManager.update_users_menu()"
        )
    else:
        nuke.menu("Nuke").addCommand(
            "Edit/Scripts Manager",
            "ScriptsManager.scripts_manager()"
        )


# Utility functions

def set_script_state_for_all_users(script_name: str, state: bool):
    """Устанавливает состояние скрипта для всех пользователей"""
    users_dir = config.USERS_DIR
    if not os.path.isdir(users_dir):
        return
    
    for user in os.listdir(users_dir):
        user_folder = os.path.join(users_dir, user)
        if not os.path.isdir(user_folder):
            continue
        
        user_manager = UserDataManager(username=user)
        if user_manager.data_file_exists():
            user_manager.set_script_state(script_name, state)


def get_default_script_state(script_name: str) -> bool:
    """Получить состояние скрипта по умолчанию."""
    info_manager = ScriptInfoManager()
    return info_manager.get_default_state(script_name)


def get_script_state(script_name: str, username: Optional[str] = None) -> bool:
    """Получить состояние скрипта для указанного пользователя (текущего если не указан)."""
    user_manager = UserDataManager(username=username)
    return user_manager.get_script_state(script_name)
