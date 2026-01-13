import nuke
import os
import ScriptsManager
import config

# Добавляем все папки внутри папки scripts в pluginPath
ScriptsManager.add_scripts_folder_to_plugin_path()

# Создаем дефолтные настройки если у пользователя нет настроек
ScriptsManager.create_user_default_settings()

# Добавляем папку пользователя в plugin path чтобы оттуда загрузились менюшки
if os.path.isdir(config.USER_FOLDER):
    nuke.pluginAddPath(config.USER_FOLDER)

# Создаем менюшки для управления скриптами
ScriptsManager.create_menu()
