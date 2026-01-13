"""
Панель для управления включением/выключением скриптов.
"""
try:
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                                   QPushButton, QCheckBox, QScrollArea, QWidget, 
                                   QLabel, QSizePolicy)
    from PySide6.QtCore import Qt
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                                      QPushButton, QCheckBox, QScrollArea, QWidget,
                                      QLabel, QSizePolicy)
        from PySide2.QtCore import Qt
        PYSIDE_VERSION = 2
    except ImportError:
        raise ImportError("Требуется PySide2 или PySide6")

from typing import Dict, List, Optional

from menu_builder import get_in_menu_name


class ScriptsManagerPanel(QDialog):
    """Панель для включения/выключения скриптов пользователем."""
    
    def __init__(self, scripts: Dict[str, str], info: Dict[str, Dict], user_data: Optional[Dict[str, bool]] = None, parent=None):
        """
        Args:
            scripts: Словарь {имя_скрипта: путь_в_меню}
            info: Словарь {имя_скрипта: {параметры}}
            user_data: Словарь {имя_скрипта: включен_ли}
            parent: Родительский виджет
        """
        super(ScriptsManagerPanel, self).__init__(parent)
        self.setWindowTitle("Scripts Manager")
        self.setMinimumSize(500, 600)
        
        self.scripts = scripts
        self.info = info
        self.user_data = user_data or {}
        self.script_checkboxes: List[QCheckBox] = []
        
        self._setup_ui()
        self._populate_scripts()
    
    def _setup_ui(self):
        """Создает интерфейс панели."""
        layout = QVBoxLayout(self)
        
        # Поиск
        search_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Фильтр...")
        self.filter_input.textChanged.connect(self._on_filter_changed)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.filter_input)
        layout.addLayout(search_layout)
        
        # Область со скриптами
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.scripts_widget = QWidget()
        self.scripts_layout = QVBoxLayout(self.scripts_widget)
        self.scripts_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.scripts_widget)
        layout.addWidget(scroll_area)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def _populate_scripts(self):
        """Заполняет список скриптов."""
        # Очищаем старые чекбоксы
        for i in reversed(range(self.scripts_layout.count())):
            item = self.scripts_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        self.script_checkboxes.clear()
        
        # Сортируем скрипты по алфавиту
        sorted_scripts = sorted(self.scripts.items(), key=lambda x: x[0].lower())
        
        for script_name, menu_path in sorted_scripts:
            # Чекбоксы создаются для существующих скриптов, но только для тех для которых есть info
            if not self.info.get(script_name):
                continue
            
            script_info = self.info[script_name]
            in_menu_name = get_in_menu_name(script_info["menu_path"], True)
            # Формируем tooltip: описание + путь в меню
            tooltip_parts = []
            if script_info.get('tooltip'):
                tooltip_parts.append(script_info['tooltip'])
            tooltip_parts.append(f"Путь: {script_info['menu_path']}")
            tooltip = "\n".join(tooltip_parts)
            
            checkbox = QCheckBox(in_menu_name)
            checkbox.setToolTip(tooltip)
            checkbox.setObjectName(script_name)  # Сохраняем имя скрипта в objectName
            
            # Устанавливаем значение из user_data или default из info
            if script_name in self.user_data:
                checkbox.setChecked(self.user_data[script_name])
            else:
                checkbox.setChecked(script_info.get("default", False))
            
            self.scripts_layout.addWidget(checkbox)
            self.script_checkboxes.append(checkbox)
    
    def _on_filter_changed(self, text: str):
        """Обработчик изменения фильтра."""
        filter_text = text.lower()
        
        for checkbox in self.script_checkboxes:
            script_name = checkbox.objectName()
            label_text = checkbox.text().lower()
            tooltip_text = checkbox.toolTip().lower()
            
            # Проверяем совпадение по имени скрипта, метке или подсказке
            matches = (
                script_name.lower().count(filter_text) > 0 or
                label_text.count(filter_text) > 0 or
                tooltip_text.count(filter_text) > 0
            )
            
            checkbox.setVisible(matches)
    
    def get_scripts_state(self) -> Dict[str, bool]:
        """
        Возвращает состояние всех скриптов.
        
        Returns:
            Словарь {имя_скрипта: включен_ли}
        """
        result = {}
        for checkbox in self.script_checkboxes:
            script_name = checkbox.objectName()
            result[script_name] = checkbox.isChecked()
        return result
    
    @staticmethod
    def show_dialog(scripts: Dict[str, str], info: Dict[str, Dict], user_data: Optional[Dict[str, bool]] = None) -> Optional[Dict[str, bool]]:
        """
        Показывает диалог и возвращает состояние скриптов, если пользователь нажал OK.
        
        Args:
            scripts: Словарь {имя_скрипта: путь_в_меню}
            info: Словарь {имя_скрипта: {параметры}}
            user_data: Словарь {имя_скрипта: включен_ли}
            
        Returns:
            Словарь {имя_скрипта: включен_ли} или None если нажата Отмена
        """
        dialog = ScriptsManagerPanel(scripts, info, user_data)
        if dialog.exec() == QDialog.Accepted:
            return dialog.get_scripts_state()
        return None
