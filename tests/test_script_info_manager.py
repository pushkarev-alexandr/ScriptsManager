"""
Тесты для ScriptInfoManager.
"""
import pytest
import sys
import os
from unittest.mock import patch

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script_info_manager import ScriptInfoManager


# Фикстура для получения пути к тестовому файлу
@pytest.fixture
def test_info_file():
    """Возвращает путь к тестовому файлу scripts_info.json."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, "test_scripts_info.json")


class TestGetScriptsInfo:
    """Тесты для метода get_scripts_info."""
    
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_get_scripts_info_success(self, mock_read_json):
        """Тест: успешное получение информации о скриптах."""
        # Настройка мока
        expected_data = {
            "script1": {"default": True},
            "script2": {"default": False}
        }
        mock_read_json.return_value = expected_data
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        result = manager.get_scripts_info()
        
        # Проверки
        assert result == expected_data
        mock_read_json.assert_called_once_with(manager.info_file, default={})
    
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_get_scripts_info_empty(self, mock_read_json):
        """Тест: получение информации, когда файл пустой."""
        # Настройка мока
        mock_read_json.return_value = {}
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        result = manager.get_scripts_info()
        
        # Проверки
        assert result == {}
        mock_read_json.assert_called_once_with(manager.info_file, default={})


class TestSaveScriptsInfo:
    """Тесты для метода save_scripts_info."""
    
    @patch('script_info_manager.write_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_save_scripts_info_success(self, mock_write_json):
        """Тест: успешное сохранение информации о скриптах."""
        # Настройка данных
        test_data = {
            "script1": {"default": True},
            "script2": {"default": False}
        }
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        manager.save_scripts_info(test_data)
        
        # Проверки
        mock_write_json.assert_called_once_with(manager.info_file, test_data)


class TestGetScriptInfo:
    """Тесты для метода get_script_info."""
    
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_get_script_info_exists(self, mock_read_json):
        """Тест: получение информации о существующем скрипте."""
        # Настройка мока
        script_name = "test_script"
        expected_info = {"default": True}
        mock_read_json.return_value = {script_name: expected_info}
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        result = manager.get_script_info(script_name)
        
        # Проверки
        assert result == expected_info
        mock_read_json.assert_called_once_with(manager.info_file, default={})
    
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_get_script_info_not_exists(self, mock_read_json):
        """Тест: получение информации о несуществующем скрипте."""
        # Настройка мока
        mock_read_json.return_value = {"other_script": {"default": True}}
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        result = manager.get_script_info("non_existent_script")
        
        # Проверки
        assert result is None
        mock_read_json.assert_called_once_with(manager.info_file, default={})


class TestUpdateScriptInfo:
    """Тесты для метода update_script_info."""
    
    @patch('script_info_manager.write_json')
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_update_script_info_new_script(self, mock_read_json, mock_write_json):
        """Тест: обновление информации о новом скрипте."""
        # Настройка моков
        mock_read_json.return_value = {}
        script_name = "new_script"
        script_info = {"default": True}
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        manager.update_script_info(script_name, script_info)
        
        # Проверки
        mock_read_json.assert_called_once_with(manager.info_file, default={})
        mock_write_json.assert_called_once_with(
            manager.info_file, 
            {script_name: script_info}
        )
    
    @patch('script_info_manager.write_json')
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_update_script_info_existing_script(self, mock_read_json, mock_write_json):
        """Тест: обновление информации о существующем скрипте."""
        # Настройка моков
        script_name = "existing_script"
        old_info = {"default": False}
        new_info = {"default": True}
        mock_read_json.return_value = {script_name: old_info}
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        manager.update_script_info(script_name, new_info)
        
        # Проверки
        mock_read_json.assert_called_once_with(manager.info_file, default={})
        mock_write_json.assert_called_once_with(
            manager.info_file, 
            {script_name: new_info}
        )


class TestRemoveScriptInfo:
    """Тесты для метода remove_script_info."""
    
    @patch('script_info_manager.write_json')
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_remove_script_info_exists(self, mock_read_json, mock_write_json):
        """Тест: удаление информации о существующем скрипте."""
        # Настройка моков
        script_name = "script_to_remove"
        other_script = "other_script"
        mock_read_json.return_value = {
            script_name: {"default": True},
            other_script: {"default": False}
        }
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        manager.remove_script_info(script_name)
        
        # Проверки
        mock_read_json.assert_called_once_with(manager.info_file, default={})
        mock_write_json.assert_called_once_with(
            manager.info_file, 
            {other_script: {"default": False}}
        )
    
    @patch('script_info_manager.write_json')
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_remove_script_info_not_exists(self, mock_read_json, mock_write_json):
        """Тест: удаление информации о несуществующем скрипте."""
        # Настройка моков
        mock_read_json.return_value = {"other_script": {"default": True}}
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        manager.remove_script_info("non_existent_script")
        
        # Проверки - write_json не должен вызываться, если скрипт не найден
        mock_read_json.assert_called_once_with(manager.info_file, default={})
        mock_write_json.assert_not_called()


class TestGetDefaultState:
    """Тесты для метода get_default_state."""
    
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_get_default_state_true(self, mock_read_json):
        """Тест: получение дефолтного состояния True."""
        # Настройка мока
        script_name = "script_with_default_true"
        mock_read_json.return_value = {
            script_name: {"default": True}
        }
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        result = manager.get_default_state(script_name)
        
        # Проверки
        assert result is True
    
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_get_default_state_false(self, mock_read_json):
        """Тест: получение дефолтного состояния False."""
        # Настройка мока
        script_name = "script_with_default_false"
        mock_read_json.return_value = {
            script_name: {"default": False}
        }
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        result = manager.get_default_state(script_name)
        
        # Проверки
        assert result is False
    
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_get_default_state_not_specified(self, mock_read_json):
        """Тест: получение дефолтного состояния, когда оно не указано."""
        # Настройка мока
        script_name = "script_without_default"
        mock_read_json.return_value = {
            script_name: {"command": "test"}  # нет ключа "default"
        }
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        result = manager.get_default_state(script_name)
        
        # Проверки - должен вернуть False по умолчанию
        assert result is False
    
    @patch('script_info_manager.read_json')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_get_default_state_script_not_exists(self, mock_read_json):
        """Тест: получение дефолтного состояния для несуществующего скрипта."""
        # Настройка мока
        mock_read_json.return_value = {}
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        result = manager.get_default_state("non_existent_script")
        
        # Проверки - должен вернуть False
        assert result is False


class TestEnsureInfoFile:
    """Тесты для метода ensure_info_file."""
    
    @patch('script_info_manager.write_json')
    @patch('script_info_manager.os.path.isfile')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_ensure_info_file_creates_when_not_exists(self, mock_isfile, mock_write_json):
        """Тест: создание файла, когда его нет."""
        # Настройка моков
        mock_isfile.return_value = False
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        manager.ensure_info_file()
        
        # Проверки
        mock_isfile.assert_called_once_with(manager.info_file)
        mock_write_json.assert_called_once_with(manager.info_file, {})
    
    @patch('script_info_manager.write_json')
    @patch('script_info_manager.os.path.isfile')
    @patch('script_info_manager.config.INFO_FILE', '/test/path/scripts_info.json')
    def test_ensure_info_file_does_not_create_when_exists(self, mock_isfile, mock_write_json):
        """Тест: не создание файла, когда он уже существует."""
        # Настройка моков
        mock_isfile.return_value = True
        
        # Создание экземпляра и вызов метода
        manager = ScriptInfoManager()
        manager.ensure_info_file()
        
        # Проверки
        mock_isfile.assert_called_once_with(manager.info_file)
        mock_write_json.assert_not_called()


# ============================================================================
# ТЕСТЫ С РЕАЛЬНЫМ ФАЙЛОМ
# ============================================================================

class TestScriptInfoManagerWithRealFile:
    """Тесты для ScriptInfoManager с использованием реального файла."""
    
    def test_get_scripts_info_from_real_file(self, test_info_file):
        """Тест: чтение информации о скриптах из реального файла."""
        # Патчим config.INFO_FILE чтобы использовать тестовый файл
        with patch('script_info_manager.config.INFO_FILE', test_info_file):
            manager = ScriptInfoManager()
            result = manager.get_scripts_info()
            
            # Проверяем, что получили данные из файла
            assert isinstance(result, dict)
            assert "test_script_1" in result
            assert "test_script_2" in result
            assert len(result) == 2
    
    def test_get_script_info_from_real_file(self, test_info_file):
        """Тест: получение информации о конкретном скрипте из реального файла."""
        with patch('script_info_manager.config.INFO_FILE', test_info_file):
            manager = ScriptInfoManager()
            
            # Получаем информацию о первом скрипте
            script_info = manager.get_script_info("test_script_1")
            assert script_info is not None
            assert script_info["default"] is True
            assert script_info["command"] == "import test_script_1; test_script_1.run()"
            assert script_info["shortcut"] == "Ctrl+1"
            
            # Получаем информацию о втором скрипте
            script_info = manager.get_script_info("test_script_2")
            assert script_info is not None
            assert script_info["default"] is False
            assert script_info["custom_cmd_checkbox"] is True
    
    def test_get_script_info_not_exists_from_real_file(self, test_info_file):
        """Тест: попытка получить информацию о несуществующем скрипте из реального файла."""
        with patch('script_info_manager.config.INFO_FILE', test_info_file):
            manager = ScriptInfoManager()
            result = manager.get_script_info("non_existent_script")
            assert result is None
    
    def test_get_default_state_from_real_file(self, test_info_file):
        """Тест: получение дефолтного состояния из реального файла."""
        with patch('script_info_manager.config.INFO_FILE', test_info_file):
            manager = ScriptInfoManager()
            
            # test_script_1 имеет default=True
            assert manager.get_default_state("test_script_1") is True
            
            # test_script_2 имеет default=False
            assert manager.get_default_state("test_script_2") is False
            
            # Несуществующий скрипт должен вернуть False
            assert manager.get_default_state("non_existent") is False
    
    def test_update_script_info_in_real_file(self, test_info_file):
        """Тест: обновление информации о скрипте в реальном файле."""
        with patch('script_info_manager.config.INFO_FILE', test_info_file):
            manager = ScriptInfoManager()
            
            # Читаем исходные данные
            original_info = manager.get_script_info("test_script_1")
            assert original_info is not None
            
            # Обновляем информацию
            updated_info = original_info.copy()
            updated_info["default"] = False
            updated_info["shortcut"] = "Ctrl+Alt+1"
            
            manager.update_script_info("test_script_1", updated_info)
            
            # Проверяем, что изменения сохранились
            saved_info = manager.get_script_info("test_script_1")
            assert saved_info["default"] is False
            assert saved_info["shortcut"] == "Ctrl+Alt+1"
            
            # Восстанавливаем исходное значение для других тестов
            manager.update_script_info("test_script_1", original_info)
    
    def test_remove_script_info_from_real_file(self, test_info_file):
        """Тест: удаление информации о скрипте из реального файла."""
        with patch('script_info_manager.config.INFO_FILE', test_info_file):
            manager = ScriptInfoManager()
            
            # Сохраняем информацию о скрипте для восстановления
            script_info = manager.get_script_info("test_script_1")
            assert script_info is not None
            
            # Удаляем скрипт
            manager.remove_script_info("test_script_1")
            
            # Проверяем, что скрипт удален
            assert manager.get_script_info("test_script_1") is None
            
            # Проверяем, что другой скрипт остался
            assert manager.get_script_info("test_script_2") is not None
            
            # Восстанавливаем удаленный скрипт для других тестов
            manager.update_script_info("test_script_1", script_info)
    
    def test_save_and_read_scripts_info_real_file(self, test_info_file):
        """Тест: сохранение и чтение информации о скриптах в реальном файле."""
        with patch('script_info_manager.config.INFO_FILE', test_info_file):
            manager = ScriptInfoManager()
            
            # Читаем исходные данные
            original_data = manager.get_scripts_info()
            assert len(original_data) == 2
            
            # Создаем новые данные
            new_data = {
                "new_script_1": {
                    "default": True,
                    "command": "import new_script_1; new_script_1.run()"
                },
                "new_script_2": {
                    "default": False,
                    "command": "import new_script_2; new_script_2.run()"
                }
            }
            
            # Сохраняем новые данные
            manager.save_scripts_info(new_data)
            
            # Проверяем, что данные сохранились
            saved_data = manager.get_scripts_info()
            assert len(saved_data) == 2
            assert "new_script_1" in saved_data
            assert "new_script_2" in saved_data
            
            # Восстанавливаем исходные данные для других тестов
            manager.save_scripts_info(original_data)
            
            # Проверяем восстановление
            restored_data = manager.get_scripts_info()
            assert len(restored_data) == 2
            assert "test_script_1" in restored_data
            assert "test_script_2" in restored_data
