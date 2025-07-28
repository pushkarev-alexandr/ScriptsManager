import nuke
import ScriptsManager

ScriptsManager.addScriptsFolderToPluginPath()  # Добавляем все папки внутри папки scripts в pluginPath для доступа к ним
ScriptsManager.createUserDefaultSettings()  # Создает дефолтные настройки если у пользователя нет настроек
nuke.pluginAddPath(ScriptsManager.userFolder)  # Добавим папку пользователя в plugin path чтобы оттуда загрузились менюшки(прошлый скрипт должен был создать папку и настройки если их не было)
ScriptsManager.createMenu()  # Создаем менюшки для управления скриптами
