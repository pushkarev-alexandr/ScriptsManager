"""
Панель для редактирования информации о скриптах.
"""
try:
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QLineEdit, QTextEdit, QComboBox, QSpinBox,
                                   QCheckBox, QPushButton, QGroupBox,
                                   QFormLayout, QScrollArea, QWidget)
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                      QLineEdit, QTextEdit, QComboBox, QSpinBox,
                                      QCheckBox, QPushButton, QGroupBox,
                                      QFormLayout, QScrollArea, QWidget)
        PYSIDE_VERSION = 2
    except ImportError:
        raise ImportError("Требуется PySide2 или PySide6")

from typing import Dict, Any, Optional
import re

import config
from menu_builder import get_in_menu_name


class EditScriptPanel(QDialog):
    """Панель для редактирования информации о скриптах."""
    
    def __init__(self, scripts: Dict[str, str], info: Dict[str, Dict[str, Any]], parent=None):
        """
        Args:
            scripts: Словарь {имя_скрипта: путь_в_меню}
            info: Словарь {имя_скрипта: {параметры}}
            parent: Родительский виджет
        """
        super(EditScriptPanel, self).__init__(parent)
        self.setWindowTitle("Edit Script")
        self.setMinimumSize(600, 500)
        
        self.scripts = scripts
        self.info = info
        self.context_list = list(config.SHORTCUT_CONTEXTS.keys())
        
        # Дефолтные значения
        self.defaults = {
            "default": False,
            "menu_name": lambda s: re.sub(r"([A-Z])", r" \1", s).strip().title(),
            "command": lambda s: f"import {s}; {s}.{s}()",
            "custom_command": "",
            "custom_cmd_checkbox": False,
            "tooltip": "",
            "icon": "",
            "shortcut": "",
            "shortcut_context": self.context_list[0],
            "index": -1,
            "menu_path": lambda s: f"{self.scripts[s]}/{self.menu_name_widget.text()}"
        }
        
        self.current_script = None
        self._setup_ui()
        self._setup_connections()
        
        # Устанавливаем первый скрипт, если есть
        if scripts:
            script_names = sorted(list(scripts.keys()))
            self.script_combo.setCurrentText(script_names[0])
            self._on_script_changed(script_names[0])
    
    def _setup_ui(self):
        """Создает интерфейс панели."""
        layout = QVBoxLayout(self)
        
        # Скроллируемая область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Выбор скрипта
        script_layout = QHBoxLayout()
        script_layout.addWidget(QLabel("Скрипт:"))
        self.script_combo = QComboBox()
        self.script_combo.addItems(sorted(list(self.scripts.keys())))
        self.script_combo.setToolTip("Скрипт который хотим добавить или изменить. Список формируется из всех файлов с расширением .py в папке scriptsDir.")
        script_layout.addWidget(self.script_combo)
        scroll_layout.addLayout(script_layout)
        
        # Основные параметры
        main_group = QGroupBox("Основные параметры")
        main_form = QFormLayout()
        
        self.default_checkbox = QCheckBox("Включен по умолчанию")
        self.default_checkbox.setToolTip("Если у пользователя нет настроек для этого скрипта, автоматом будет устанавливаться в True. Также при загрузке нюка если у пользователя совсем нет настроек, то этот скрипт сразу добавится пользователю")
        main_form.addRow(self.default_checkbox)
        
        self.custom_cmd_checkbox = QCheckBox("Кастомная команда")
        self.custom_cmd_checkbox.setToolTip("Включит режим в котором нужно самому ввести команду которая будет выполняться при запуске программы и создавать меню или назначать колбэки")
        main_form.addRow(self.custom_cmd_checkbox)
        
        main_group.setLayout(main_form)
        scroll_layout.addWidget(main_group)
        
        # Параметры стандартного меню
        standard_group = QGroupBox("Параметры стандартного меню")
        standard_form = QFormLayout()
        
        self.menu_name_widget = QLineEdit()
        self.menu_name_widget.setToolTip("Имя которое будет отображаться в меню для вызова скрипта")
        standard_form.addRow("Имя в меню:", self.menu_name_widget)
        
        self.command_widget = QLineEdit()
        self.command_widget.setToolTip("Команда которая будет выполняться при нажатии на кнопку вызова скрипта")
        standard_form.addRow("Команда:", self.command_widget)
        
        self.tooltip_widget = QTextEdit()
        self.tooltip_widget.setMaximumHeight(60)
        self.tooltip_widget.setToolTip("Описание скрипта которое будет показываться при наведении мышки на скрипт в меню Script Manager")
        standard_form.addRow("Описание:", self.tooltip_widget)
        
        self.icon_widget = QLineEdit()
        self.icon_widget.setToolTip("Иконка для менюшки скрипта. Нужно писать с расширением, к примеру icon.png")
        standard_form.addRow("Иконка:", self.icon_widget)
        
        self.shortcut_widget = QLineEdit()
        self.shortcut_widget.setToolTip("Горячая клавиша для вызова скрипта")
        standard_form.addRow("Горячая клавиша:", self.shortcut_widget)
        
        self.shortcut_context_combo = QComboBox()
        self.shortcut_context_combo.addItems(self.context_list)
        self.shortcut_context_combo.setToolTip("Контекст вызова горячей клавиши:\n0 - Window\n1 - Application\n2 - DAG")
        standard_form.addRow("Контекст:", self.shortcut_context_combo)
        
        self.index_widget = QSpinBox()
        self.index_widget.setMinimum(-1)
        self.index_widget.setMaximum(1000)
        self.index_widget.setValue(-1)
        self.index_widget.setToolTip("Положение где будет находиться кнопка вызова скрипта в меню. Значение -1 означает что скрипт будет добавлен в конец меню")
        standard_form.addRow("Положение (индекс):", self.index_widget)
        
        self.menu_path_label = QLabel()
        self.menu_path_label.setToolTip("Путь до скрипта в меню")
        standard_form.addRow("Путь в меню:", self.menu_path_label)
        
        standard_group.setLayout(standard_form)
        scroll_layout.addWidget(standard_group)
        self.standard_group = standard_group
        
        # Кастомная команда
        custom_group = QGroupBox("Кастомная команда")
        custom_form = QFormLayout()
        
        self.custom_command_widget = QTextEdit()
        self.custom_command_widget.setMinimumHeight(100)
        self.custom_command_widget.setToolTip("Команда которая будет прописана в menu.py файле пользователя и будет выполняться при запуске программы")
        custom_form.addRow("Команда:", self.custom_command_widget)
        
        custom_group.setLayout(custom_form)
        scroll_layout.addWidget(custom_group)
        custom_group.setVisible(False)
        self.custom_group = custom_group
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)
        
        layout.addLayout(buttons_layout)
    
    def _setup_connections(self):
        """Настраивает соединения сигналов."""
        self.script_combo.currentTextChanged.connect(self._on_script_changed)
        self.menu_name_widget.textChanged.connect(self._on_menu_name_changed)
        self.command_widget.textChanged.connect(self._on_command_changed)
        self.custom_cmd_checkbox.toggled.connect(self._on_custom_command_toggled)
    
    def _on_script_changed(self, script_name: str):
        """Обработчик изменения выбранного скрипта."""
        self.current_script = script_name
        script_info = self.info.get(script_name)
        
        if script_info:
            # Загружаем данные из info
            self.default_checkbox.setChecked(script_info.get("default", False))
            self.custom_cmd_checkbox.setChecked(script_info.get("custom_cmd_checkbox", False))
            
            menu_path = script_info.get("menu_path", "")
            if menu_path:
                self.menu_name_widget.setText(get_in_menu_name(menu_path, False))
                self.menu_path_label.setText(f"{self.scripts.get(script_name, '')}/{self.menu_name_widget.text()}")
            
            self.command_widget.setText(script_info.get("command", ""))
            self.custom_command_widget.setPlainText(script_info.get("custom_command", ""))
            self.tooltip_widget.setPlainText(script_info.get("tooltip", ""))
            self.icon_widget.setText(script_info.get("icon", ""))
            self.shortcut_widget.setText(script_info.get("shortcut", ""))
            
            context = script_info.get("shortcut_context", self.context_list[0])
            index = self.context_list.index(context) if context in self.context_list else 0
            self.shortcut_context_combo.setCurrentIndex(index)
            
            self.index_widget.setValue(script_info.get("index", -1))
        else:
            # Устанавливаем дефолтные значения
            self._set_defaults(script_name)
        
        self._on_custom_command_toggled(self.custom_cmd_checkbox.isChecked())
    
    def _set_defaults(self, script_name: str):
        """Устанавливает дефолтные значения для скрипта."""
        self.default_checkbox.setChecked(self.defaults["default"])
        self.custom_cmd_checkbox.setChecked(self.defaults["custom_cmd_checkbox"])
        
        menu_name = self.defaults["menu_name"](script_name) if callable(self.defaults["menu_name"]) else ""
        self.menu_name_widget.setText(menu_name)
        
        command = self.defaults["command"](script_name) if callable(self.defaults["command"]) else ""
        self.command_widget.setText(command)
        
        self.custom_command_widget.setPlainText(self.defaults["custom_command"])
        self.tooltip_widget.setPlainText(self.defaults["tooltip"])
        self.icon_widget.setText(self.defaults["icon"])
        self.shortcut_widget.setText(self.defaults["shortcut"])
        self.shortcut_context_combo.setCurrentText(self.defaults["shortcut_context"])
        self.index_widget.setValue(self.defaults["index"])
        
        menu_path = f"{self.scripts.get(script_name, '')}/{menu_name}"
        self.menu_path_label.setText(menu_path)
    
    def _on_menu_name_changed(self, text: str):
        """Обработчик изменения имени в меню."""
        if self.current_script:
            menu_path = f"{self.scripts.get(self.current_script, '')}/{text}"
            self.menu_path_label.setText(menu_path)
    
    def _on_command_changed(self, text: str):
        """Обработчик изменения команды - заменяем одинарные кавычки на двойные."""
        if "'" in text:
            new_text = text.replace("'", '"')
            self.command_widget.blockSignals(True)
            self.command_widget.setText(new_text)
            self.command_widget.blockSignals(False)
    
    def _on_custom_command_toggled(self, enabled: bool):
        """Обработчик переключения режима кастомной команды."""
        # Показываем/скрываем соответствующие группы
        self.custom_group.setVisible(enabled)
        self.standard_group.setVisible(not enabled)
    
    def get_script_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о текущем скрипте.
        
        Returns:
            Словарь с информацией о скрипте
        """
        script_name = self.script_combo.currentText()
        menu_path = f"{self.scripts.get(script_name, '')}/{self.menu_name_widget.text()}"
        
        return {
            "default": self.default_checkbox.isChecked(),
            "custom_cmd_checkbox": self.custom_cmd_checkbox.isChecked(),
            "menu_name": self.menu_name_widget.text(),
            "menu_path": menu_path,
            "command": self.command_widget.text(),
            "custom_command": self.custom_command_widget.toPlainText(),
            "tooltip": self.tooltip_widget.toPlainText(),
            "icon": self.icon_widget.text(),
            "shortcut": self.shortcut_widget.text(),
            "shortcut_context": self.shortcut_context_combo.currentText(),
            "index": self.index_widget.value()
        }
    
    @staticmethod
    def show_dialog(scripts: Dict[str, str], info: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Показывает диалог и возвращает информацию о скрипте, если пользователь нажал OK.
        
        Args:
            scripts: Словарь {имя_скрипта: путь_в_меню}
            info: Словарь {имя_скрипта: {параметры}}
            
        Returns:
            Кортеж (имя_скрипта, информация) или None если нажата Отмена
        """
        dialog = EditScriptPanel(scripts, info)
        if dialog.exec() == QDialog.Accepted:
            script_name = dialog.script_combo.currentText()
            script_info = dialog.get_script_info()
            # Удаляем menu_name, так как оно содержится в menu_path
            script_info.pop("menu_name", None)
            return script_name, script_info
        return None
