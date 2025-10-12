import nuke, nukescripts
import os, json, getpass, re

curDir = os.path.dirname(__file__).replace("\\", "/")  # Текущая папка
infoFile = f"{curDir}/scripts_info.json"  # Необходимая информация о скриптах, заполняется в edit_script_info
scriptsDir = f"{os.path.dirname(curDir)}/scripts"  # Папка где лежат все скрипты
userFolder = f"{curDir}/users/{getpass.getuser()}"  # С этой папки происходит загрузка менюшек для пользователя, у каждого пользователя своя папка
userDataFile = f"{userFolder}/data.json"  # Информация о включенных/выключенных скриптах пользователя
userMenuFile = f"{userFolder}/menu.py"  # Файл который будет создавать менюшки для пользователя
scripts_manager_users = ["apushkarev", "pushk", "kzolototrubov"]  # Пользователи для которых создается менюшка для редактирования скриптов добавления и удаления информации о них

def get_scripts(addToPluginPath=False):
    """
    Возвращает словарь со всеми найденными скриптами.

    Ключом словаря является имя скрипта (без расширения .py),
    а значением - путь, где скрипт будет находиться в меню Nuke.
    Если addToPluginPath равно True, то каждая папка, содержащая скрипты,
    будет добавлена в Nuke's pluginPath. Это полезно, если новые скрипты
    были добавлены во время работы Nuke, и их папки еще не были в pluginPath.
    """
    scripts = {}
    for fileDir, _, files in os.walk(scriptsDir):
        for file in files:
            if file.endswith(".py"):
                menu_path = fileDir[len(scriptsDir)+1:].replace("\\", "/")  # И пути до папки отбрасываем путь до папки scripts чтобы получить путь в менюшке
                script_name = os.path.splitext(file)[0]  # Отбрасываем .py
                scripts[script_name] = menu_path
        if addToPluginPath:
            nuke.pluginAddPath(fileDir.replace("\\", "/"))
    return scripts

def writeAndAddMenu(file, info, createMenus=False):
    """
    Записывает меню в файл и создает меню в Nuke
    Args:
        file: Файл, в который будет записано меню
        info: Информация о скрипте
        createMenus: Флаг, указывающий, нужно ли создавать меню в Nuke. Если False то только записывать данные в файл,
                     по умолчанию False потомучто используется чаще в скриптах где создание меню не требуется
    """
    if info["custom_cmd_checkbox"]:  # Смотрим с помощью чего будем создавать меню, с помощью обычных параметров или через кастомное меню
        file.write(info["custom_command"] + "\n")  # Записываем кастомную команду
        if createMenus:  # Сразу выполняем код если необходимо
            try:
                exec(info["custom_command"])
            except Exception as e:
                nuke.message(f"Не получилось выполнить текущую команду(\n{e}")
    else:
        menu_path, command, icon, shortcut, context, index = [info[n] for n in ["menu_path", "command", "icon", "shortcut", "shortcut_context", "index"]]  # Не делаем проверок, предпологаем что необходимые параметры есть в базе
        if context in ["0", "1", "2"]:  # Если нужно указать определенный контекст
            file.write(f"nuke.menu('Nuke').addCommand('{menu_path}', '{command}', '{shortcut}', icon='{icon}', index={index}, shortcutContext={context})\n")
            if createMenus:
                nuke.menu("Nuke").addCommand(menu_path, command, shortcut, icon=icon, index=index, shortcutContext=int(context))
        else:
            file.write(f"nuke.menu('Nuke').addCommand('{menu_path}', '{command}', '{shortcut}', icon='{icon}', index={index})\n")
            if createMenus:
                nuke.menu("Nuke").addCommand(menu_path, command, shortcut, icon=icon, index=index)

class ScriptsManagerPanel(nukescripts.PythonPanel):
    """Kласс для окна включения/выключения скриптов пользователем"""
    def __init__(self, scripts, info, userData):
        nukescripts.PythonPanel.__init__(self, "Scripts Manager")
        self.filter = nuke.String_Knob("filter", "")
        self.addKnob(self.filter)
        self.addKnob(nuke.PyScript_Knob("filter_button", "filter"))
        self.scripts_knobs = []  # Кнобы отвечающие за скрипты
        for scr in scripts:  # Проходимся по каждому скрипту в алфавитном порядке
            if info.get(scr):  # Если есть информация о скрипте
                menu_path = info[scr]["menu_path"]
                kn = nuke.Boolean_Knob(scr, menu_path.split("/")[-1])  # Создаем для него кноб
                kn.setFlag(nuke.STARTLINE)
                if userData and userData.get(scr)!=None:  # Если уже есть записанные данные для пользователя, подставим их
                    kn.setValue(userData[scr])
                kn.setTooltip(f"{info[scr]['tooltip']}\n<i>{menu_path}</i>")  # Установим подсказку что делает скрипт
                self.addKnob(kn)
                self.scripts_knobs.append(kn)  # Добавим кноб в список кнобов которые потом надо обработать
    
    def knobChanged(self, kn):
        if kn.name()=="filter_button":
            filter = self.filter.value().lower()
            for kn in self.scripts_knobs:
                if kn.name().lower().count(filter) or kn.label().lower().count(filter) or kn.tooltip().lower().count(filter):
                    kn.setVisible(True)
                else:
                    kn.setVisible(False)

def removeMenu(info: dict):
    """Удаляет меню при выключении скрипта в scripts_manager"""
    menu_paths = []
    if info["custom_cmd_checkbox"]:
        for line in info["custom_command"].split("\n"):  # Команды разделены по строкам
            if line.count(".addCommand(")==1:
                menu_path = line.split(".addCommand(")[1].split(",")[0].strip("'").strip('"')
                menu_paths.append(menu_path)
    else:
        menu_paths.append(info["menu_path"])
    for menu_path in menu_paths:
        spl = menu_path.split("/")  # Полный путь
        menu = "/".join(spl[:-1])  # Путь до меню где лежит кнопка скрипта
        m = nuke.menu("Nuke").menu(menu)
        if not m:  # Если такого меню не нашли будем искать просто в меню Nuke
            m = nuke.menu("Nuke")
        # Делаем проверку что это Menu, потому что например Cache/Localization это MenuItem, а у MenuItem нету функции findItem
        if isinstance(m, nuke.Menu) and m.findItem(spl[-1]):  # Если нашли кнопку, удалим ее
            m.removeItem(spl[-1])
        baseMenu = nuke.menu("Nuke").findItem(spl[0])  # Базовая папка меню(Udmurtia, File)
        if not isinstance(baseMenu, nuke.Menu):  # Если в меню не осталось скриптов, оно становится MenuItem и тогда надо его удалить
            nuke.menu("Nuke").removeItem(spl[0])

def scripts_manager():
    """Главное меню для включения/выключения плагинов"""
    if not os.path.isfile(infoFile):  # Проверяем существует ли scripts_info.json без него невозможно работать
        nuke.message("Нужен файл scripts_info.json")
        return
    info, userData = [None, None]
    with open(infoFile, "r", encoding="utf-8") as file:  # Читаем данные из info файла
        info = json.load(file)
    if not info:  # Проверяем что удалось что-то прочитать из info
        nuke.message("Ошибка чтения файла scripts_info.json")
        return
    if os.path.isfile(userDataFile):  # Если есть файл для пользователя, тоже читаем данные
        with open(userDataFile, "r", encoding="utf-8") as file:
            userData = json.load(file)
    scripts = get_scripts(True)  # Получаем все доступные скрипты в алфавитном порядке
    if not scripts:
        nuke.message("Не нашел ни одного скрипта в папке scripts")
        return
    panel = ScriptsManagerPanel(scripts, info, userData)  # Запускаем панель
    if not panel.showModalDialog():  # Если была нажата кнопка отмены выходим из скрипта
        return
    if not os.path.isdir(userFolder):  # Если нету папки для пользователя, создадим ее
        os.makedirs(userFolder)
    data = {}
    file = open(userMenuFile, "w", encoding="utf-8")
    for kn in panel.scripts_knobs:
        scr = kn.name()
        data[scr] = kn.value()  # Записываем включил или выключил пользователь скрипт
        if kn.value():
            writeAndAddMenu(file, info[scr], True)
        else:
            removeMenu(info[scr])
    file.close()
    with open(userDataFile, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    nuke.message("Скрипты успешно изменены!\n(возможно потребуется перезагрузить Nuke)")

class EditScriptPanel(nukescripts.PythonPanel):
    """Класс для окна с редактированием информации о скриптах"""
    def __init__(self, scripts: dict, info: dict):
        """
        Args:
            scripts (dict): Словарь с именем скрипта и путем до менюшки где он должен лежать
            info (dict): Информация о скриптах: команда, горячая клавиша и т.д.
        """
        nukescripts.PythonPanel.__init__(self, "Edit Script")
        self.setMinimumSize(550, 350)  # Увеличиваем окно
        self.scripts = scripts  # Записываем в локальные переменные для дальнейшего доступа к ним
        self.info = info
        context_list = ["Без контекста", "0", "1", "2"]  # Список параметров для кноба shortcut_context
        # Дефолтные значения для кнобов, в lambda s подается имя скрипта script
        self.defaults = {"default": False,
                         "menu_name": lambda s: re.sub(r"([A-Z])", r" \1", s).strip().title(),
                         "command": lambda s: f"import {s}; {s}.{s}()",
                         "custom_command": "",
                         "custom_cmd_checkbox": False,
                         "tooltip": "",
                         "icon": "",
                         "shortcut": "",
                         "shortcut_context": context_list[0],
                         "index": -1,
                         "menu_path": lambda s: f"{self.scripts[s]}/{self.knobs()['menu_name'].value()}"}
        # Описание всех необходимых кнобов
        self.script = nuke.Enumeration_Knob("script", "Скрипт", list(scripts.keys()))
        self.script.setTooltip("Скрипт который хотим добавить или изменить. Список формируется из всех файлов с расширением .py в папке scriptsDir.")
        self.default = nuke.Boolean_Knob("default", "Включен по умолчанию")
        self.default.setTooltip("Если у пользователя нет настроек для этого скрипта, автоматом будет устанавливаться в True. Также при загрузке нюка если у пользователя совсем нет настроек, то этот скрипт сразу добавится пользователю")
        self.default.setFlag(nuke.STARTLINE)
        self.custom_cmd_checkbox = nuke.Boolean_Knob("custom_cmd_checkbox", "Кастомная команда")
        self.custom_cmd_checkbox.setTooltip("Включит режим в котором нужно самому ввести команду которая будет выполняться при запуске программы и создавать меню или назначать колбэки")
        self.menu_name = nuke.String_Knob("menu_name", "Имя в меню")
        self.menu_name.setTooltip("Имя которое будет отображаться в меню для вызова скрипта")
        self.command = nuke.String_Knob("command", "Команда")
        self.command.setTooltip("Команда которая будет выполняться при нажатии на кнопку вызова скрипта")
        self.custom_command = nuke.Multiline_Eval_String_Knob("custom_command", "Команда")
        self.custom_command.setTooltip("Команда которая будет прописана в menu.py файле пользователя и будет выполняться при запуске программы. Может как создавать меню, произвольного количества и с произвольным поведением не зависящим от параметров этого меню, так и к примеру задавать колбэки.")
        self.tooltip = nuke.Multiline_Eval_String_Knob("tooltip", "Описание")
        self.tooltip.setTooltip("Описание скрипта которое будет показываться при наведении мышки на скрипт в меню Script Manager")
        self.icon = nuke.String_Knob("icon", "Иконка")
        self.icon.setTooltip("Иконка для менюшки скрипта. Нужно писать с расширением, к примеру <b>icon.png</b> Расширение никак не контролируется, что будет написано в этом поле, то и подставится. Поэтому нужно следить за тем что расширение указано.")
        self.shortcut = nuke.String_Knob("shortcut", "Горячая клавиша")
        self.shortcut.setTooltip("Горячая клавиша для вызова скрипта")
        self.shortcut_context = nuke.Enumeration_Knob("shortcut_context", "Контекст", context_list)
        self.shortcut_context.setTooltip("Контекст вызова горячей клавиши:\n<b>0</b> Window\n<b>1</b> Application\n<b>2</b> DAG\nНужно выбрать 2 когда нужно чтобы горячая клавиша работала только в нодграфе и не работала во вьювере.\nВ таком случае возможно понадобится обозначать горячие клавиши через:\n<b>^</b> Ctrl\n<b>#</b> Alt\n<b>+</b> Shift")
        self.index = nuke.Int_Knob("index", "Положение(индекс)")
        self.index.setTooltip("Положение где будет находиться кнопка вызова скрипта в меню. К примеру можно добавить скрипт в меню File на вторую позицию. Значение -1 означает что скрипт будет добавлен в конец меню")
        self.menu_path = nuke.Text_Knob("menu_path", "Путь в меню")
        self.menu_path.setTooltip("Путь до скрипта в меню")
        self.my_knobs = [self.script, self.default, self.custom_cmd_checkbox, self.menu_name, self.command, self.custom_command, self.tooltip, self.icon, self.shortcut, self.shortcut_context, self.index, self.menu_path]  # Порядок добавления кнобов в меню
        for kn in self.my_knobs:
            self.addKnob(kn)
        self.my_knobs.insert(1, self.my_knobs.pop(3))  # Перемещаем menu_name на вторую позицию чтобы позже игнорировать этот кноб как и script
        self.setupKnobValues()  # Выставляем значение для кнобов
    
    def knobChanged(self, kn):
        if kn.name()=="script":
            self.setupKnobValues()
        elif kn.name()=="menu_name":  # Когда меняем имя скрипта в меню, то путь до меню берем из self.scripts
            self.menu_path.setValue(f"{self.scripts[self.script.value()]}/{self.menu_name.value()}")
        elif kn.name()=="command":
            kn.setValue(kn.value().replace("'",'"'))  # Одинарные кавычки заменяем на двойные, это важно для writeAndAddMenu потомучто там используются одинарные
        elif kn.name()=="custom_cmd_checkbox":
            self.disableKnobsIfCustomCommand()
    
    def setFromDefaults(self, kn, scr):
        """Выставляет для кноба kn значение из словаря self.defaults"""
        default = self.defaults.get(kn.name())
        if callable(default):
            kn.setValue(default(scr))
        elif default!=None:
            kn.setValue(default)
    
    def disableKnobsIfCustomCommand(self):
        """Включает/выключает определенные кнобы если включена галка custom_cmd_checkbox"""
        enable = self.custom_cmd_checkbox.value()
        for kn in ["menu_name", "command", "icon", "shortcut", "shortcut_context", "index", "menu_path"]:
            self.knobs()[kn].setVisible(not enable)
        self.knobs()["custom_command"].setVisible(enable)

    def setupKnobValues(self):
        """Выставляет значения для кнобов из файла scripts_info.json, если нету, то дефолтные"""
        scr = self.script.value()  # Текущий выбранный скрипт, для которого нужно выставить настройки
        info = self.info.get(scr)  # Информация для текущего скрипта
        if info:  # Если уже есть запись для скрипта в scripts_info.json, выставим ее
            for kn in self.my_knobs[2:-1]:  # Все кроме названия скрипта(он уже установлен), menu_name(его нету в info, он берется из menu_path) и menu_path(оно берется из self.scripts)
                if info.get(kn.name())!=None:  # Проверяем что такой кноб есть в info(на случай если мы добавили новый кноб, которого не было раньше)
                    kn.setValue(info[kn.name()])
                else:
                    self.setFromDefaults(kn,scr)  # Если не удалось найти параметр в info, установим значение по умолчанию
            self.menu_name.setValue(info["menu_path"].split("/")[-1])  # Выставляем menu_name из menu_path
            self.menu_path.setValue(f"{self.scripts[scr]}/{self.menu_name.value()}")  # Затем выставляем menu_path из scripts(на случай если мы переместили скрипт в новое место)
        else:  # Дефолтные значения для кнобов
            for kn in self.my_knobs[1:]:  # Для каждого кноба ищем дефолтное значение
                self.setFromDefaults(kn, scr)
        self.disableKnobsIfCustomCommand()

def edit_script_info():
    """Добавляет/изменяет информацию о скрипте в файле scripts_info.json."""
    scripts = get_scripts()  # Получаем все доступные скрипты в алфавитном порядке
    if not scripts:
        nuke.message("Не нашел ни одного скрипта в папке scripts")
        return
    if not os.path.isfile(infoFile):  # Создаем файл scripts_info.json если его не существует
        with open(infoFile, "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4, ensure_ascii=False)
    with open(infoFile, "r", encoding="utf-8") as file:  # Читаем данные из info файла
        info = json.load(file)
    p = EditScriptPanel(scripts, info)
    if p.showModalDialog():  # Если пользователь нажал OK
        info[p.my_knobs[0].value()] = {kn.name(): kn.value() for kn in p.my_knobs[2:]}  # menu_name мы не записываем, потому что оно содержится в menu_path
        with open(infoFile, "w", encoding="utf-8") as file:  # Записываем данные в файл
            json.dump(info, file, indent=4, ensure_ascii=False)
        updateUsersMenu()

def remove_script_info():
    """
    Удаляет запись о скрипте в файле scripts_info.json.
    При этом у пользователей этот скрипт не удалится, но он больше не появится
    в списке выбора Scripts Manager. Просто когда пользователь пойдет настраивать
    свои скрипты, они у него обновятся и скрипт пропадет.
    """
    if not os.path.isfile(infoFile):
        nuke.message("Нужен файл scripts_info.json")
        return
    with open(infoFile, "r", encoding="utf-8") as file:  # Читаем данные из info файла
        info: dict = json.load(file)
    p = nuke.Panel("Remove Script")
    p.addEnumerationPulldown("Script", " ".join(list(info)))
    if p.show():
        info.pop(p.value("Script"))
        with open(infoFile, "w", encoding="utf-8") as file:
            json.dump(info, file, indent=4, ensure_ascii=False)
        updateUsersMenu()  # Обновляем настройки у пользователей, чтобы убрать только что удаленные скрипты

def createUserDefaultSettings(userDataFile=userDataFile, userMenuFile=userMenuFile):
    """
    При загрузке Nuke создает для пользователя дефолтные настройки, если у него их еще нет.
    Это нужно, чтобы при первой загрузке у пользователя уже были необходимые скрипты,
    такие как `ReadFromWrite` и `Reveal in Folder`. По умолчанию функция выполняется
    для текущего пользователя, но можно передать `userDataFile` и `userMenuFile`
    для кастомного пользователя (используется в `updateUsersMenu`).
    """
    # Если настройки есть, ничего делать не нужно. Если нет хотя бы одного файла, будем один создавать, другой перезаписывать.
    if os.path.isfile(userDataFile) and os.path.isfile(userMenuFile):
        return
    scripts = get_scripts()  # Получаем все доступные скрипты в алфавитном порядке
    if not scripts:  # Если никаких скриптов нету, выходим из функции
        return
    if not os.path.isfile(infoFile):  # Проверяем существует ли scripts_info.json, в нем хранится информация о дефолтных скриптах
        return
    with open(infoFile, "r", encoding="utf-8") as file:  # Читаем данные из info файла
        info = json.load(file)
    if not os.path.isdir(userFolder):  # Если нету папки для пользователя, создадим ее
        os.makedirs(userFolder)
    data = {}
    file = open(userMenuFile, "w", encoding="utf-8")  # Запишем дефолтные менюшки для пользователя
    for scr in scripts:  # Проходимся по всем скриптам
        if info.get(scr) is None:  # Проверяем что для скрипта есть информация
            continue
        data[scr] = info[scr]["default"]  # Записываем включен или выключен плагин
        if info[scr]["default"]:  # Если это дефолтный скрипт, его нужно добавить в menu.py файл
            writeAndAddMenu(file, info[scr])  # Не создаем меню сразу, потому что создаем файл menu.py и меню будет создано автоматически из файла
    file.close()
    with open(userDataFile, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def updateUsersMenu():
    """
    Для всех пользователей в папке users заново создает menu.py.
    Создание происходит на основе включенных скриптов в userDataFile и новой
    информации из scripts_info.json, которой у пользователя еще нет.
    Если у пользователя нет файла data.json или menu.py, они будут созданы
    с помощью `createUserDefaultSettings`. Эта функция вызывается в `edit_script_info`
    после изменения информации о скриптах и в `remove_script_info` чтобы
    обновить удаленные скрипты.
    """
    scripts = get_scripts()  # Получаем все доступные скрипты в алфавитном порядке
    if not scripts:  # Если никаких скриптов нету, выходим из функции
        return
    if not os.path.isfile(infoFile):  # Проверяем существует ли scripts_info.json
        return
    with open(infoFile, "r", encoding="utf-8") as file:  # Читаем данные из info файла
        info = json.load(file)
    users_dir = f"{curDir}/users"
    if not os.path.isdir(users_dir):  # Нужно проверить что существует папка с пользователями, перед следующей операцией os.listdir
        return
    for user in os.listdir(users_dir):  # Проходимся по папкам и файлам в папке со всеми пользователями
        user_folder = f"{users_dir}/{user}"
        if os.path.isdir(user_folder):  # Проверяем что это папка а не файл
            user_data_file = f"{user_folder}/data.json"
            user_menu_file = f"{user_folder}/menu.py"
            if os.path.isfile(user_data_file) and os.path.isfile(user_menu_file):  # Проверяем что есть оба файла настроек
                with open(user_data_file, "r", encoding="utf-8") as file:
                    userData = json.load(file)  # Информация о включенных/выключенных скриптах, к ней в итоге добавим новую инфу или удалим то что уже не актуально
                data = {}  # Новая data которую мы запишем в userDataFile
                file = open(user_menu_file, "w", encoding="utf-8")
                for scr in scripts:  # Проходимся по всем скриптам
                    if info.get(scr) is None:  # Проверяем что для скрипта есть информация (если нету, этот скрипт не будет добавлен в menu.py пользователю, даже если он был там до этого).
                        continue
                    # Нужно понять мы добавляем скрипт в menu или нет, понять это можно через уже существующий userData или если в нем нет записи, посмотреть в default.
                    enable = userData.get(scr)
                    if enable is None:
                        enable = info[scr]["default"]
                    data[scr] = enable
                    if enable:
                        writeAndAddMenu(file, info[scr])  # Не создаем меню потому что записываем menu.py не для текущего пользователя, меню будет создано у пользователя при запуске нюка.
                file.close()
                with open(user_data_file, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
            else:
                createUserDefaultSettings(user_data_file, user_menu_file)  # Создаем файлы настроек с нуля, добавляя только дефолтные скрипты
                # Эта функция повторяет функционал только что выполненный текущей функцией, к примеру получение скриптов scripts = get_scripts() и проверка на существование необходимых файлов.
                # Но так как этот код выполняется не при загрузке скрипта, то мы можем проигнорировать оптимизацию и скорость выполнения этого скрипта.
    nuke.message("Successfully updated!")

def addScriptsFolderToPluginPath():
    """
    Добавляет все папки внутри папки scripts в pluginPath для доступа к ним.
    """
    for root, _, _ in os.walk(scriptsDir):  # Если папки не существует ошибки не будет, просто не запустится цикл
        if os.path.basename(root) not in ["__pycache__"]:
            nuke.pluginAddPath(root.replace("\\", "/"))

def createMenu():
    """
    Создает меню для управления скриптами.
    Для обычных пользователей это просто включение и выключение скриптов.
    Для избранных пользователей из списка `scripts_manager_users` еще и меню
    для управления информацией о скриптах и удаления информации о скриптах.
    """
    if getpass.getuser() in scripts_manager_users:
        nuke.menu("Nuke").addCommand("Edit/Scripts Manager/Scripts Manager", "ScriptsManager.scripts_manager()")  # Позволяет включать и выключать скрипты
        nuke.menu("Nuke").addCommand("Edit/Scripts Manager/Edit Scripts Info", "ScriptsManager.edit_script_info()")  # Добавление/изменение информации о скрипте
        nuke.menu("Nuke").addCommand("Edit/Scripts Manager/Remove Script", "ScriptsManager.remove_script_info()")  # Удаление скриптов
        nuke.menu("Nuke").addCommand("Edit/Scripts Manager/Update Users Menus", "ScriptsManager.updateUsersMenu()")  # Обновляет настройки для всех пользователей
    else:
        nuke.menu("Nuke").addCommand("Edit/Scripts Manager", "ScriptsManager.scripts_manager()")  # Позволяет включать и выключать скрипты

# utility functions

def setScriptStateForAllUsers(name: str, state: bool):
    """Полезно когда нужно сразу всем пользователям поменять включен или выключен плагин"""
    users_dir = f"{curDir}/users"
    if not os.path.isdir(users_dir):  # Нужно проверить что существует папка с пользователями, перед следующей операцией os.listdir
        return
    for user in os.listdir(users_dir):  # Проходимся по папкам и файлам в папке со всеми пользователями
        user_folder = f"{users_dir}/{user}"
        if os.path.isdir(user_folder):  # Проверяем что это папка а не файл
            user_data_file = f"{user_folder}/data.json"
            if os.path.isfile(user_data_file):  # Проверяем что есть файл настроек
                with open(user_data_file, "r", encoding="utf-8") as file:
                    userData = json.load(file)
                if name in userData:
                    userData[name] = state
                    with open(user_data_file, "w", encoding="utf-8") as file:
                        json.dump(userData, file, indent=4, ensure_ascii=False)

def get_default_script_state(script_name: str) -> bool:
    """Получить состояние скрипта по умолчанию. Если информации нет, вернуть False."""
    if not os.path.isfile(infoFile):
        return False  # По умолчанию выключен
    with open(infoFile, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data.get(script_name, False)

def get_script_state(script_name: str, username: str = None) -> bool:
    """Получить состояние скрипта для указанного пользователя(текущего если не указан)."""
    if username is None:
        username = getpass.getuser()
    userDataFile = f"{curDir}/users/{username}/data.json"
    if os.path.isfile(userDataFile):
        with open(userDataFile, "r", encoding="utf-8") as file:
            data = json.load(file)
            if script_name in data:
                return data[script_name]
    
    return get_default_script_state(script_name)
