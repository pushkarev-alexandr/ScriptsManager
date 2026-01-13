"""
Тесты для UserDataManager.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_data_manager import UserDataManager


# Фикстура для получения пути к тестовому файлу
@pytest.fixture
def test_data_file():
    """Возвращает путь к тестовому файлу данных пользователя."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, "test_user_data.json")


class TestInit:
    """Тесты для метода __init__."""
    
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_init_with_default_username(self):
        """Тест: инициализация с username по умолчанию."""
        manager = UserDataManager()
        
        assert manager.username == 'test_user'
        assert manager.user_folder == '/test/users/test_user'
        assert manager.data_file == '/test/users/test_user/data.json'
        assert manager.menu_file == '/test/users/test_user/menu.py'
    
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_init_with_custom_username(self):
        """Тест: инициализация с указанным username."""
        manager = UserDataManager(username='custom_user')
        
        assert manager.username == 'custom_user'
        assert manager.user_folder == '/test/users/custom_user'
        assert manager.data_file == '/test/users/custom_user/data.json'
        assert manager.menu_file == '/test/users/custom_user/menu.py'


class TestGetUserData:
    """Тесты для метода get_user_data."""
    
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_get_user_data_success(self, mock_read_json):
        """Тест: успешное получение данных пользователя."""
        # Настройка мока
        expected_data = {
            "script1": True,
            "script2": False
        }
        mock_read_json.return_value = expected_data
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.get_user_data()
        
        # Проверки
        assert result == expected_data
        mock_read_json.assert_called_once_with(manager.data_file, default={})
    
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_get_user_data_empty(self, mock_read_json):
        """Тест: получение данных, когда файл пустой."""
        # Настройка мока
        mock_read_json.return_value = {}
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.get_user_data()
        
        # Проверки
        assert result == {}
        mock_read_json.assert_called_once_with(manager.data_file, default={})
    
    def test_get_user_data_from_real_file(self, test_data_file):
        """Тест: чтение данных пользователя из реального файла."""
        # Используем реальный read_json без моков для чтения тестового файла
        # Патчим только config, чтобы указать путь к тестовому файлу
        test_dir = os.path.dirname(test_data_file)
        
        with patch('user_data_manager.config.USERNAME', 'test_user'), \
             patch('user_data_manager.config.USERS_DIR', test_dir):
            
            manager = UserDataManager()
            # Устанавливаем data_file на тестовый файл напрямую
            manager.data_file = test_data_file
            
            # Вызываем метод без мока read_json - используем реальную функцию
            result = manager.get_user_data()
            
            # Проверяем, что получили данные из файла
            assert isinstance(result, dict)
            assert "test_script_1" in result
            assert "test_script_2" in result
            assert "test_script_3" in result
            assert result["test_script_1"] is True
            assert result["test_script_2"] is False
            assert result["test_script_3"] is True
            assert len(result) == 3
    
    def test_get_user_data_from_nonexistent_file(self):
        """Тест: чтение данных пользователя из несуществующего файла."""
        # Используем реальный read_json без моков - он сам обрабатывает несуществующий файл
        with patch('user_data_manager.config.USERNAME', 'nonexistent_user'), \
             patch('user_data_manager.config.USERS_DIR', '/nonexistent/path/to'):
            
            manager = UserDataManager()
            result = manager.get_user_data()
            
            # Проверяем, что вернулся пустой словарь (default значение)
            # read_json автоматически вернет default={} для несуществующего файла
            assert result == {}


class TestSaveUserData:
    """Тесты для метода save_user_data."""
    
    @patch('user_data_manager.write_json')
    @patch('user_data_manager.ensure_dir')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_save_user_data_success(self, mock_ensure_dir, mock_write_json):
        """Тест: успешное сохранение данных пользователя."""
        # Настройка данных
        test_data = {
            "script1": True,
            "script2": False
        }
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        manager.save_user_data(test_data)
        
        # Проверки
        mock_ensure_dir.assert_called_once_with(manager.user_folder)
        mock_write_json.assert_called_once_with(manager.data_file, test_data)
    
    @patch('user_data_manager.write_json')
    @patch('user_data_manager.ensure_dir')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_save_user_data_empty(self, mock_ensure_dir, mock_write_json):
        """Тест: сохранение пустых данных."""
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        manager.save_user_data({})
        
        # Проверки
        mock_ensure_dir.assert_called_once_with(manager.user_folder)
        mock_write_json.assert_called_once_with(manager.data_file, {})


class TestGetScriptState:
    """Тесты для метода get_script_state."""
    
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_get_script_state_from_user_data(self, mock_read_json):
        """Тест: получение состояния скрипта из данных пользователя."""
        # Настройка мока
        script_name = "test_script"
        mock_read_json.return_value = {script_name: True}
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.get_script_state(script_name)
        
        # Проверки
        assert result is True
        mock_read_json.assert_called_once_with(manager.data_file, default={})
    
    @patch('user_data_manager.ScriptInfoManager')
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_get_script_state_from_default(self, mock_read_json, mock_script_info_manager_class):
        """Тест: получение состояния скрипта из дефолтных значений (False)."""
        # Настройка моков
        script_name = "test_script"
        mock_read_json.return_value = {}  # Нет данных пользователя
        
        mock_script_info_manager = MagicMock()
        mock_script_info_manager.get_default_state.return_value = False
        mock_script_info_manager_class.return_value = mock_script_info_manager
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.get_script_state(script_name)
        
        # Проверки
        assert result is False
        mock_read_json.assert_called_once_with(manager.data_file, default={})
        mock_script_info_manager.get_default_state.assert_called_once_with(script_name)
    
    @patch('user_data_manager.ScriptInfoManager')
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_get_script_state_from_default_true(self, mock_read_json, mock_script_info_manager_class):
        """Тест: получение состояния скрипта из дефолтных значений (True)."""
        # Настройка моков
        script_name = "test_script"
        mock_read_json.return_value = {}  # Нет данных пользователя
        
        mock_script_info_manager = MagicMock()
        mock_script_info_manager.get_default_state.return_value = True
        mock_script_info_manager_class.return_value = mock_script_info_manager
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.get_script_state(script_name)
        
        # Проверки
        assert result is True
        mock_read_json.assert_called_once_with(manager.data_file, default={})
        mock_script_info_manager.get_default_state.assert_called_once_with(script_name)
    
    @patch('user_data_manager.ScriptInfoManager')
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_get_script_state_user_data_overrides_default(self, mock_read_json, mock_script_info_manager_class):
        """Тест: данные пользователя переопределяют дефолтные значения."""
        # Настройка моков
        script_name = "test_script"
        mock_read_json.return_value = {script_name: True}  # Пользователь установил True
        
        mock_script_info_manager = MagicMock()
        mock_script_info_manager.get_default_state.return_value = False  # Дефолт False
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.get_script_state(script_name)
        
        # Проверки - должно вернуться значение из данных пользователя
        assert result is True
        # ScriptInfoManager не должен вызываться, если есть данные пользователя
        mock_script_info_manager.get_default_state.assert_not_called()


class TestSetScriptState:
    """Тесты для метода set_script_state."""
    
    @patch('user_data_manager.write_json')
    @patch('user_data_manager.ensure_dir')
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_set_script_state_enabled(self, mock_read_json, mock_ensure_dir, mock_write_json):
        """Тест: установка состояния скрипта как включенного."""
        # Настройка моков
        script_name = "test_script"
        mock_read_json.return_value = {}
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        manager.set_script_state(script_name, True)
        
        # Проверки
        mock_read_json.assert_called_once_with(manager.data_file, default={})
        mock_ensure_dir.assert_called_once_with(manager.user_folder)
        mock_write_json.assert_called_once_with(manager.data_file, {script_name: True})
    
    @patch('user_data_manager.write_json')
    @patch('user_data_manager.ensure_dir')
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_set_script_state_disabled(self, mock_read_json, mock_ensure_dir, mock_write_json):
        """Тест: установка состояния скрипта как выключенного."""
        # Настройка моков
        script_name = "test_script"
        mock_read_json.return_value = {"other_script": True}
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        manager.set_script_state(script_name, False)
        
        # Проверки
        mock_read_json.assert_called_once_with(manager.data_file, default={})
        mock_ensure_dir.assert_called_once_with(manager.user_folder)
        mock_write_json.assert_called_once_with(
            manager.data_file, 
            {"other_script": True, script_name: False}
        )
    
    @patch('user_data_manager.write_json')
    @patch('user_data_manager.ensure_dir')
    @patch('user_data_manager.read_json')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_set_script_state_updates_existing(self, mock_read_json, mock_ensure_dir, mock_write_json):
        """Тест: обновление существующего состояния скрипта."""
        # Настройка моков
        script_name = "test_script"
        mock_read_json.return_value = {script_name: False}
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        manager.set_script_state(script_name, True)
        
        # Проверки
        mock_read_json.assert_called_once_with(manager.data_file, default={})
        mock_ensure_dir.assert_called_once_with(manager.user_folder)
        mock_write_json.assert_called_once_with(manager.data_file, {script_name: True})


class TestEnsureUserFolder:
    """Тесты для метода ensure_user_folder."""
    
    @patch('user_data_manager.ensure_dir')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_ensure_user_folder(self, mock_ensure_dir):
        """Тест: создание папки пользователя."""
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        manager.ensure_user_folder()
        
        # Проверки
        mock_ensure_dir.assert_called_once_with(manager.user_folder)


class TestMenuFileExists:
    """Тесты для метода menu_file_exists."""
    
    @patch('user_data_manager.os.path.isfile')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_menu_file_exists_true(self, mock_isfile):
        """Тест: файл меню существует."""
        # Настройка мока
        mock_isfile.return_value = True
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.menu_file_exists()
        
        # Проверки
        assert result is True
        mock_isfile.assert_called_once_with(manager.menu_file)
    
    @patch('user_data_manager.os.path.isfile')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_menu_file_exists_false(self, mock_isfile):
        """Тест: файл меню не существует."""
        # Настройка мока
        mock_isfile.return_value = False
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.menu_file_exists()
        
        # Проверки
        assert result is False
        mock_isfile.assert_called_once_with(manager.menu_file)


class TestDataFileExists:
    """Тесты для метода data_file_exists."""
    
    @patch('user_data_manager.os.path.isfile')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_data_file_exists_true(self, mock_isfile):
        """Тест: файл данных существует."""
        # Настройка мока
        mock_isfile.return_value = True
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.data_file_exists()
        
        # Проверки
        assert result is True
        mock_isfile.assert_called_once_with(manager.data_file)
    
    @patch('user_data_manager.os.path.isfile')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_data_file_exists_false(self, mock_isfile):
        """Тест: файл данных не существует."""
        # Настройка мока
        mock_isfile.return_value = False
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        result = manager.data_file_exists()
        
        # Проверки
        assert result is False
        mock_isfile.assert_called_once_with(manager.data_file)


class TestWriteMenuFile:
    """Тесты для метода write_menu_file."""
    
    @patch('user_data_manager.write_text_file')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_write_menu_file_success(self, mock_write_text_file):
        """Тест: успешная запись файла меню."""
        # Настройка данных
        content = "def menu():\n    pass"
        
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        manager.write_menu_file(content)
        
        # Проверки
        mock_write_text_file.assert_called_once_with(manager.menu_file, content)
    
    @patch('user_data_manager.write_text_file')
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_write_menu_file_empty(self, mock_write_text_file):
        """Тест: запись пустого файла меню."""
        # Создание экземпляра и вызов метода
        manager = UserDataManager()
        manager.write_menu_file("")
        
        # Проверки
        mock_write_text_file.assert_called_once_with(manager.menu_file, "")


# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestUserDataManagerIntegration:
    """Интеграционные тесты для UserDataManager."""
    
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_get_set_script_state_flow(self):
        """Тест: полный цикл получения и установки состояния скрипта."""
        with patch('user_data_manager.read_json') as mock_read_json, \
             patch('user_data_manager.write_json') as mock_write_json, \
             patch('user_data_manager.ensure_dir') as mock_ensure_dir:
            
            # Начальное состояние - нет данных пользователя
            mock_read_json.return_value = {}
            
            manager = UserDataManager()
            
            # Устанавливаем состояние скрипта
            manager.set_script_state("script1", True)
            
            # Проверяем, что данные были сохранены
            assert mock_write_json.called
            call_args = mock_write_json.call_args
            assert call_args[0][1] == {"script1": True}
            
            # Симулируем чтение сохраненных данных
            mock_read_json.return_value = {"script1": True}
            
            # Получаем состояние скрипта
            state = manager.get_script_state("script1")
            assert state is True
    
    @patch('user_data_manager.config.USERNAME', 'test_user')
    @patch('user_data_manager.config.USERS_DIR', '/test/users')
    def test_multiple_scripts_management(self):
        """Тест: управление несколькими скриптами."""
        with patch('user_data_manager.read_json') as mock_read_json, \
             patch('user_data_manager.write_json') as mock_write_json, \
             patch('user_data_manager.ensure_dir'):
            
            manager = UserDataManager()
            
            # Устанавливаем состояния для нескольких скриптов
            mock_read_json.return_value = {}
            manager.set_script_state("script1", True)
            
            mock_read_json.return_value = {"script1": True}
            manager.set_script_state("script2", False)
            
            # Проверяем, что оба скрипта сохранены
            final_call = mock_write_json.call_args_list[-1]
            final_data = final_call[0][1]
            assert "script1" in final_data
            assert "script2" in final_data
            assert final_data["script1"] is True
            assert final_data["script2"] is False
