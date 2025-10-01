#!/usr/bin/env python3
"""
Скрипт для управления менеджерами проектов в Planka
Позволяет добавлять менеджера ко всем проектам через API
"""
import requests
import os
from typing import Optional
from plankapy import Planka, PasswordAuth
from planka_client import PlankaClient
import logging
from dotenv import load_dotenv


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()


def get_api_token(base_url: str, username: str, password: str) -> Optional[str]:
    """
    Получает API токен из Planka через аутентификацию
    
    Args:
        base_url: Базовый URL Planka (например, https://planka.example.com)
        username: Имя пользователя или email
        password: Пароль пользователя
    
    Returns:
        API токен или None в случае ошибки
    """
    try:
        # Убираем trailing slash если есть
        base_url = base_url.rstrip('/')
        
        # Аутентификация через API
        auth_url = f"{base_url}/api/access-tokens"
        response = requests.post(
            auth_url,
            data={
                'emailOrUsername': username,
                'password': password
            }
        )
        
        if response.status_code == 200:
            token = response.json().get('item')
            print(f"✓ API токен успешно получен")
            return token
        else:
            print(f"✗ Ошибка получения токена: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Ошибка при получении токена: {e}")
        return None


def save_api_key_to_env(api_key: str, env_file_path: str = '.env') -> bool:
    """
    Saves the API key to the .env file.
    
    Args:
        api_key: The API key to save
        env_file_path: Path to the .env file (default: .env)
    
    Returns:
        True if successful, False otherwise
    """
    import re
    try:
        # Read current .env content
        env_content = ""
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                env_content = f.read()
        
        # Check if PLANKA_API_KEY already exists
        if 'PLANKA_API_KEY=' in env_content:
            # Update existing key
            env_content = re.sub(r'PLANKA_API_KEY=.*', f'PLANKA_API_KEY={api_key}', env_content)
        else:
            # Add new key
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f'PLANKA_API_KEY={api_key}\n'
        
        # Write back to .env file
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        
        print(f"✓ API ключ сохранен в {env_file_path}")
        return True
    except Exception as e:
        print(f"✗ Ошибка при сохранении API ключа в .env: {e}")
        return False


def display_projects(planka: Planka) -> None:
    """
    Отображает список всех проектов
    
    Args:
        planka: Экземпляр Planka API
    """
    projects = planka.projects
    
    if not projects:
        print("\n⚠ Проекты не найдены")
        return
    
    print(f"\n{'='*60}")
    print(f"СПИСОК ПРОЕКТОВ (Всего: {len(projects)})")
    print(f"{'='*60}")
    
    for idx, project in enumerate(projects, 1):
        managers = project.managers
        manager_names = [m.name or m.username for m in managers]
        
        print(f"\n{idx}. {project.name}")
        print(f"   ID: {project.id}")
        print(f"   Менеджеры ({len(managers)}): {', '.join(manager_names) if manager_names else 'Нет менеджеров'}")


def display_users(planka: Planka) -> None:
    """
    Отображает список всех пользователей
    
    Args:
        planka: Экземпляр Planka API
    """
    users = planka.users
    
    if not users:
        print("\n⚠ Пользователи не найдены")
        return
    
    print(f"\n{'='*60}")
    print(f"СПИСОК ПОЛЬЗОВАТЕЛЕЙ (Всего: {len(users)})")
    print(f"{'='*60}")
    
    for idx, user in enumerate(users, 1):
        print(f"{idx}. {user.name or user.username} (@{user.username})")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print()


def select_operation() -> str:
    """
    Меню выбора операции
    
    Returns:
        Выбранная операция
    """
    print(f"\n{'='*60}")
    print("ВЫБЕРИТЕ ОПЕРАЦИЮ")
    print(f"{'='*60}")
    print("1. Добавить менеджера ко всем проектам")
    print("2. Показать список проектов")
    print("3. Показать список пользователей")
    print("4. Выход")
    
    choice = input("\nВведите номер операции: ").strip()
    
    operations = {
        '1': 'add_manager_all',
        '2': 'show_projects',
        '3': 'show_users',
        '4': 'exit'
    }
    
    return operations.get(choice, 'invalid')


def select_user(planka: Planka) -> Optional[object]:
    """
    Позволяет пользователю выбрать менеджера из списка
    
    Args:
        planka: Экземпляр Planka API
    
    Returns:
        Выбранный пользователь или None
    """
    users = planka.users
    
    if not users:
        print("\n⚠ Пользователи не найдены")
        return None
    
    print(f"\n{'='*60}")
    print("ВЫБЕРИТЕ ПОЛЬЗОВАТЕЛЯ ДЛЯ ДОБАВЛЕНИЯ КАК МЕНЕДЖЕРА")
    print(f"{'='*60}")
    
    for idx, user in enumerate(users, 1):
        print(f"{idx}. {user.name or user.username} (@{user.username}) - {user.email}")
    
    while True:
        try:
            choice = input(f"\nВведите номер пользователя (1-{len(users)}) или 'q' для отмены: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            idx = int(choice) - 1
            
            if 0 <= idx < len(users):
                selected_user = users[idx]
                print(f"\n✓ Выбран пользователь: {selected_user.name or selected_user.username}")
                return selected_user
            else:
                print(f"✗ Неверный номер. Введите число от 1 до {len(users)}")
                
        except ValueError:
            print("✗ Введите корректное число")


def add_manager_to_all_projects(planka: PlankaClient, manager: object) -> None:
    """
    Добавляет менеджера ко всем проектам
    
    Args:
        planka: Экземпляр PlankaClient API
        manager: Объект пользователя для добавления как менеджера
    """
    projects = planka.projects
    
    if not projects:
        print("\n⚠ Проекты не найдены")
        return
    
    print(f"\n{'='*60}")
    print(f"ДОБАВЛЕНИЕ МЕНЕДЖЕРА КО ВСЕМ ПРОЕКТАМ")
    print(f"{'='*60}")
    print(f"Менеджер: {manager.name or manager.username}")
    print(f"Количество проектов: {len(projects)}")
    
    confirm = input("\nПродолжить? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("✗ Операция отменена")
        return
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    print("\nДобавление менеджера к проектам:")
    
    for project in projects:
        try:
            # Проверяем, является ли пользователь уже менеджером
            existing_managers = [m.id for m in project.managers]
            
            if manager.id in existing_managers:
                print(f"  ⊙ {project.name}: Уже является менеджером")
                skip_count += 1
            else:
                # Добавляем менеджера к проекту через прямой API вызов
                url = f"{planka.api_url}/projects/{project.id}/project-managers"
                headers = {
                    "Authorization": f"Bearer {planka.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "userId": manager.id
                }
                
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code in [200, 201]:
                    print(f"  ✓ {project.name}: Успешно добавлен")
                    success_count += 1
                    # Обновляем проект для получения актуальной информации
                    project.refresh()
                else:
                    logger.error(f"Error adding manager to project {project.name}: HTTP {response.status_code} - {response.text}")
                    print(f"  ✗ {project.name}: Ошибка HTTP {response.status_code}")
                    error_count += 1
                
        except Exception as e:
            print(f"  ✗ {project.name}: Ошибка - {e}")
            logger.error(f"Exception adding manager to project {project.name}: {e}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print("РЕЗУЛЬТАТЫ:")
    print(f"  Успешно добавлено: {success_count}")
    print(f"  Пропущено (уже менеджер): {skip_count}")
    print(f"  Ошибок: {error_count}")
    print(f"{'='*60}")


def main():
    """
    Главная функция программы
    """
    print(f"{'='*60}")
    print("УПРАВЛЕНИЕ МЕНЕДЖЕРАМИ ПРОЕКТОВ PLANKA")
    print(f"{'='*60}")
    PLANKA_URL = os.getenv('PLANKA_URL', 'https://planka.mad-auto.ru/')
    
    # Check if API key already exists
    API_KEY = os.getenv('PLANKA_API_KEY')
    
    # If no API key is found in environment, request new one and save it
    if not API_KEY or API_KEY == 'your_api_key_here':
        print("API ключ не найден в .env файле или использует значение по умолчанию.")
        base_url = PLANKA_URL  # Using default URL
        username = input("Введите имя пользователя или email: ").strip()
        password = input("Введите пароль: ").strip()
        
        print("\n⌛ Получение API токена...")
        
        api_token = get_api_token(base_url, username, password)
        
        if api_token:
            print(f"API Token (первые 20 символов): {api_token[:20]}...")
            # Save the new API key to .env file
            if save_api_key_to_env(api_token):
                API_KEY = api_token
                print("✓ API ключ сохранен в .env файл")
            else:
                print("✗ Не удалось сохранить API ключ в .env файл")
                return
        else:
            print("✗ Не удалось получить API токен")
            return
    else:
        print("✓ Используем существующий API ключ из .env файла")
    
    # Аутентификация через PlankaClient
    try:
        planka = PlankaClient(PLANKA_URL, API_KEY)
        
        # Проверка подключения
        current_user = planka.me
        print(f"✓ Успешно подключено как: {current_user.name or current_user.username}")
        
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return
    
    # Главный цикл программы
    while True:
        operation = select_operation()
        
        if operation == 'add_manager_all':
            # Выбор менеджера
            manager = select_user(planka)
            
            if manager:
                # Добавление менеджера ко всем проектам
                add_manager_to_all_projects(planka, manager)
            else:
                print("\n✗ Операция отменена")
        
        elif operation == 'show_projects':
            display_projects(planka)
        
        elif operation == 'show_users':
            display_users(planka)
        
        elif operation == 'exit':
            print("\n👋 До свидания!")
            break
        
        else:
            print("\n✗ Неверный выбор. Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
