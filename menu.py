#v1.5
import nuke
import ScriptsManager

ScriptsManager.addScriptsFolderToPluginPath()#добавляем все папки внутри папки scripts в pluginPath для доступа к ним
ScriptsManager.createUserDefaultSettings()#создает дефолтные настройки если у пользователя нет настроек
nuke.pluginAddPath(ScriptsManager.userFolder)#добавим папку пользователя в plugin path чтобы оттуда загрузились менюшки(прошлый скрипт должен был создать папку и настройки если их не было)
ScriptsManager.createMenu()#создаем менюшки для управления скриптами