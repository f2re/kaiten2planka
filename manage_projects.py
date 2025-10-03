#!/usr/bin/env python3
"""
Скрипт для управления менеджерами проектов в Planka
Позволяет добавлять менеджера ко всем проектам через API
И перемещать доски между проектами
"""
import requests
import os
from typing import Optional, List, Dict, Any
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
        base_url = base_url.rstrip('/')
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
    """
    import re
    try:
        env_content = ""
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                env_content = f.read()
        
        if 'PLANKA_API_KEY=' in env_content:
            env_content = re.sub(r'PLANKA_API_KEY=.*', f'PLANKA_API_KEY={api_key}', env_content)
        else:
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f'PLANKA_API_KEY={api_key}\n'
        
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        
        print(f"✓ API ключ сохранен в {env_file_path}")
        return True
    except Exception as e:
        print(f"✗ Ошибка при сохранении API ключа в .env: {e}")
        return False


def get_board_details(planka: PlankaClient, board_id: str) -> Optional[Dict[str, Any]]:
    """
    Получает полную информацию о доске включая списки и карточки
    
    Args:
        planka: Экземпляр PlankaClient API
        board_id: ID доски
    
    Returns:
        Словарь с информацией о доске или None
    """
    try:
        url = f"{planka.api_url}/boards/{board_id}"
        headers = {
            "Authorization": f"Bearer {planka.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error getting board details: HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception getting board details: {e}")
        return None


def create_board_in_project(planka: PlankaClient, project_id: str, board_name: str, position: int = 0) -> Optional[Dict[str, Any]]:
    """
    Создает новую доску в проекте
    
    Args:
        planka: Экземпляр PlankaClient API
        project_id: ID целевого проекта
        board_name: Название новой доски
        position: Позиция доски
    
    Returns:
        Данные созданной доски или None
    """
    try:
        url = f"{planka.api_url}/projects/{project_id}/boards"
        headers = {
            "Authorization": f"Bearer {planka.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "name": board_name,
            "position": position
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Error creating board: HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception creating board: {e}")
        return None


def create_list_in_board(planka: PlankaClient, board_id: str, list_name: str, position: int = 0) -> Optional[Dict[str, Any]]:
    """
    Создает список в доске
    КРИТИЧНО: API требует параметр 'type' для создания списков
    
    Args:
        planka: Экземпляр PlankaClient API
        board_id: ID доски
        list_name: Название списка
        position: Позиция списка
    
    Returns:
        Данные созданного списка или None
    """
    try:
        url = f"{planka.api_url}/boards/{board_id}/lists"
        headers = {
            "Authorization": f"Bearer {planka.api_key}",
            "Content-Type": "application/json"
        }
        
        # Обрабатываем null/None имена списков
        if not list_name or (isinstance(list_name, str) and list_name.strip() == ''):
            list_name = 'Unnamed List'
            logger.warning(f"List has null/empty name, using 'Unnamed List'")
        
        data = {
            "name": list_name,
            "position": position,
            "type": "normal"  # ОБЯЗАТЕЛЬНЫЙ параметр для API Planka!
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Error creating list '{list_name}': HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception creating list '{list_name}': {e}")
        return None


def create_card_in_list(planka: PlankaClient, board_id: str, list_id: str, card_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Создает карточку в списке
    
    Args:
        planka: Экземпляр PlankaClient API
        board_id: ID доски
        list_id: ID списка
        card_data: Данные карточки
    
    Returns:
        Данные созданной карточки или None
    """
    try:
        url = f"{planka.api_url}/boards/{board_id}/cards"
        headers = {
            "Authorization": f"Bearer {planka.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "listId": list_id,
            "name": card_data.get('name', 'Untitled'),
            "position": card_data.get('position', 0),
        }
        
        # Добавляем опциональные поля если они есть
        if 'description' in card_data and card_data['description']:
            data['description'] = card_data['description']
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Error creating card '{card_data.get('name')}': HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception creating card '{card_data.get('name')}': {e}")
        return None


def delete_board(planka: PlankaClient, board_id: str) -> bool:
    """
    Удаляет доску
    
    Args:
        planka: Экземпляр PlankaClient API
        board_id: ID доски для удаления
    
    Returns:
        True если успешно, False при ошибке
    """
    try:
        url = f"{planka.api_url}/boards/{board_id}"
        headers = {
            "Authorization": f"Bearer {planka.api_key}",
        }
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 204]:
            return True
        else:
            logger.error(f"Error deleting board: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception deleting board: {e}")
        return False


def move_board_with_content(planka: PlankaClient, board: object, target_project: object, 
                           rename_prefix: Optional[str] = None, delete_source: bool = True) -> bool:
    """
    Перемещает доску со всем содержимым в другой проект
    ВАЖНО: Удаление исходной доски происходит ТОЛЬКО после успешного копирования ВСЕХ данных
    
    Args:
        planka: Экземпляр PlankaClient API
        board: Объект доски для перемещения
        target_project: Целевой проект
        rename_prefix: Префикс для переименования доски
        delete_source: Удалить исходную доску после копирования
    
    Returns:
        True если успешно, False при ошибке
    """
    try:
        # Получаем полную информацию о доске
        board_details = get_board_details(planka, board.id)
        if not board_details:
            logger.error(f"Failed to get board details for {board.id}")
            return False
        
        # Формируем новое имя доски
        new_board_name = f"{rename_prefix} - {board.name}" if rename_prefix else board.name
        
        # Получаем позицию доски, используя 0 если None
        board_position = board.position if board.position is not None else 0
        
        # Создаем новую доску в целевом проекте
        new_board = create_board_in_project(planka, target_project.id, new_board_name, position=board_position)
        if not new_board:
            logger.error(f"Failed to create board in target project")
            return False
        
        new_board_id = new_board['item']['id']
        logger.info(f"Created new board {new_board_id} with name '{new_board_name}'")
        
        # Получаем списки из исходной доски
        lists = board_details.get('included', {}).get('lists', [])
        
        if not lists:
            logger.warning(f"No lists found in board {board.id}")
        
        list_mapping = {}  # Маппинг старых ID списков на новые
        lists_created = 0
        
        # Создаем списки в новой доске с обработкой None в position
        sorted_lists = sorted(lists, key=lambda x: x.get('position', 0) if x.get('position') is not None else 0)
        
        for list_item in sorted_lists:
            list_name = list_item.get('name')
            
            # КРИТИЧНО: Обрабатываем null/None имена списков
            if not list_name:
                list_name = 'Unnamed List'
                logger.warning(f"List with ID {list_item.get('id')} has null name, using 'Unnamed List'")
            
            list_position = list_item.get('position', 0) if list_item.get('position') is not None else 0
            new_list = create_list_in_board(
                planka, 
                new_board_id, 
                list_name, 
                list_position
            )
            if new_list:
                old_list_id = list_item['id']
                new_list_id = new_list['item']['id']
                list_mapping[old_list_id] = new_list_id
                lists_created += 1
                logger.info(f"Created list '{list_name}' - mapping {old_list_id} -> {new_list_id}")
            else:
                logger.error(f"Failed to create list '{list_name}'")
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА: если есть списки но не создались, не продолжаем
        if lists and lists_created == 0:
            logger.error(f"CRITICAL: No lists were created! Aborting operation. Original board NOT deleted.")
            logger.error(f"Deleting incomplete board {new_board_id}")
            delete_board(planka, new_board_id)
            return False
        
        # Получаем карточки из исходной доски
        cards = board_details.get('included', {}).get('cards', [])
        
        if not cards:
            logger.warning(f"No cards found in board {board.id}")
        
        # Создаем карточки в новой доске с обработкой None в position
        sorted_cards = sorted(cards, key=lambda x: x.get('position', 0) if x.get('position') is not None else 0)
        
        created_cards = 0
        skipped_cards = 0
        
        for card in sorted_cards:
            old_list_id = card.get('listId')
            new_list_id = list_mapping.get(old_list_id)
            
            if new_list_id:
                card_position = card.get('position', 0) if card.get('position') is not None else 0
                card_data = {
                    'name': card.get('name', 'Untitled'),
                    'description': card.get('description'),
                    'position': card_position
                }
                result = create_card_in_list(planka, new_board_id, new_list_id, card_data)
                if result:
                    created_cards += 1
                    logger.info(f"Created card '{card_data['name']}' in list {new_list_id}")
                else:
                    logger.error(f"Failed to create card '{card_data['name']}'")
            else:
                skipped_cards += 1
                logger.warning(f"Could not find mapping for list {old_list_id}, skipping card '{card.get('name')}'")
        
        # Детальный отчет о миграции
        logger.info(f"Migration summary: {lists_created}/{len(lists)} lists created, {created_cards}/{len(cards)} cards created, {skipped_cards} cards skipped")
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА: проверяем успешность операции перед удалением
        success_threshold = 0.7  # 70% успешности
        
        if lists:
            list_success_rate = lists_created / len(lists)
        else:
            list_success_rate = 1.0
        
        if cards:
            card_success_rate = created_cards / len(cards) if created_cards > 0 else 0.0
        else:
            card_success_rate = 1.0
        
        overall_success = (list_success_rate + card_success_rate) / 2
        
        logger.info(f"Success rate: lists={list_success_rate:.1%}, cards={card_success_rate:.1%}, overall={overall_success:.1%}")
        
        if overall_success < success_threshold:
            logger.error(f"CRITICAL: Migration success rate ({overall_success:.1%}) below threshold ({success_threshold:.0%})")
            logger.error(f"Original board ID: {board.id} - NOT DELETED")
            logger.error(f"New incomplete board ID: {new_board_id} - KEPT for review")
            print(f"\n⚠ ПРЕДУПРЕЖДЕНИЕ: Миграция не завершена! Исходная доска сохранена.")
            print(f"   Исходная доска ID: {board.id}")
            print(f"   Новая доска ID: {new_board_id}")
            return False
        
        # Удаляем исходную доску ТОЛЬКО если копирование прошло успешно
        if delete_source:
            logger.info(f"Migration successful ({overall_success:.1%}). Proceeding to delete source board {board.id}")
            if delete_board(planka, board.id):
                logger.info(f"Source board {board.id} deleted successfully")
            else:
                logger.error(f"FAILED to delete source board {board.id}. Manual cleanup required.")
                logger.error(f"Original board ID: {board.id}, New board ID: {new_board_id}")
                print(f"\n⚠ Не удалось удалить исходную доску {board.id}. Требуется ручная очистка.")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Exception moving board with content: {e}", exc_info=True)
        return False


def display_projects(planka: Planka) -> None:
    """Отображает список всех проектов"""
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
        boards = project.boards
        
        print(f"\n{idx}. {project.name}")
        print(f"   ID: {project.id}")
        print(f"   Менеджеры ({len(managers)}): {', '.join(manager_names) if manager_names else 'Нет менеджеров'}")
        print(f"   Досок: {len(boards)}")
        if boards:
            for board in boards:
                print(f"      - {board.name} (ID: {board.id})")


def display_users(planka: Planka) -> None:
    """Отображает список всех пользователей"""
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
    """Меню выбора операции"""
    print(f"\n{'='*60}")
    print("ВЫБЕРИТЕ ОПЕРАЦИЮ")
    print(f"{'='*60}")
    print("1. Добавить менеджера ко всем проектам")
    print("2. Показать список проектов")
    print("3. Показать список пользователей")
    print("4. Переместить доски из проекта в другой проект")
    print("5. Переместить все доски из всех проектов в один проект")
    print("6. Выход")
    
    choice = input("\nВведите номер операции: ").strip()
    
    operations = {
        '1': 'add_manager_all',
        '2': 'show_projects',
        '3': 'show_users',
        '4': 'move_boards',
        '5': 'consolidate_boards',
        '6': 'exit'
    }
    
    return operations.get(choice, 'invalid')


def select_user(planka: Planka) -> Optional[object]:
    """Позволяет пользователю выбрать менеджера из списка"""
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


def select_project(planka: Planka, prompt: str = "ВЫБЕРИТЕ ПРОЕКТ") -> Optional[object]:
    """Позволяет пользователю выбрать проект из списка"""
    projects = planka.projects
    
    if not projects:
        print("\n⚠ Проекты не найдены")
        return None
    
    print(f"\n{'='*60}")
    print(prompt)
    print(f"{'='*60}")
    
    for idx, project in enumerate(projects, 1):
        boards = project.boards
        print(f"{idx}. {project.name} ({len(boards)} досок)")
    
    while True:
        try:
            choice = input(f"\nВведите номер проекта (1-{len(projects)}) или 'q' для отмены: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            idx = int(choice) - 1
            
            if 0 <= idx < len(projects):
                selected_project = projects[idx]
                print(f"\n✓ Выбран проект: {selected_project.name}")
                return selected_project
            else:
                print(f"✗ Неверный номер. Введите число от 1 до {len(projects)}")
                
        except ValueError:
            print("✗ Введите корректное число")


def move_boards_between_projects(planka: PlankaClient) -> None:
    """Интерактивное перемещение досок из одного проекта в другой"""
    print(f"\n{'='*60}")
    print("ПЕРЕМЕЩЕНИЕ ДОСОК МЕЖДУ ПРОЕКТАМИ")
    print(f"{'='*60}")
    
    source_project = select_project(planka, "ВЫБЕРИТЕ ИСХОДНЫЙ ПРОЕКТ")
    if not source_project:
        print("✗ Операция отменена")
        return
    
    if not source_project.boards:
        print(f"\n⚠ В проекте '{source_project.name}' нет досок")
        return
    
    target_project = select_project(planka, "ВЫБЕРИТЕ ЦЕЛЕВОЙ ПРОЕКТ")
    if not target_project:
        print("✗ Операция отменена")
        return
    
    if source_project.id == target_project.id:
        print("✗ Исходный и целевой проект совпадают")
        return
    
    print(f"\n📋 Доски из проекта '{source_project.name}':")
    for idx, board in enumerate(source_project.boards, 1):
        print(f"  {idx}. {board.name}")
    
    rename = input(f"\nДобавить префикс '{source_project.name}' к названиям досок? (y/n): ").strip().lower()
    prefix = source_project.name if rename == 'y' else None
    
    confirm = input(f"\nПереместить {len(source_project.boards)} досок в проект '{target_project.name}'? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("✗ Операция отменена")
        return
    
    success_count = 0
    error_count = 0
    
    print("\nПеремещение досок (копирование со всем содержимым):")
    
    boards_list = list(source_project.boards)  # Создаем копию списка
    for board in boards_list:
        print(f"\n  Обработка доски: {board.name}")
        if move_board_with_content(planka, board, target_project, prefix, delete_source=True):
            new_name = f"{prefix} - {board.name}" if prefix else board.name
            print(f"  ✓ {board.name} → {new_name} (со всеми списками и карточками)")
            success_count += 1
        else:
            print(f"  ✗ {board.name}: Ошибка перемещения")
            error_count += 1
    
    print(f"\n{'='*60}")
    print("РЕЗУЛЬТАТЫ:")
    print(f"  Успешно перемещено: {success_count}")
    print(f"  Ошибок: {error_count}")
    print(f"{'='*60}")


def consolidate_all_boards(planka: PlankaClient) -> None:
    """Перемещает все доски из всех проектов в один целевой проект"""
    print(f"\n{'='*60}")
    print("КОНСОЛИДАЦИЯ ВСЕХ ДОСОК В ОДИН ПРОЕКТ")
    print(f"{'='*60}")
    
    projects = planka.projects
    
    if not projects or len(projects) < 2:
        print("\n⚠ Недостаточно проектов для консолидации")
        return
    
    target_project = select_project(planka, "ВЫБЕРИТЕ ЦЕЛЕВОЙ ПРОЕКТ ДЛЯ ВСЕХ ДОСОК")
    if not target_project:
        print("✗ Операция отменена")
        return
    
    total_boards = 0
    boards_by_project = {}
    
    for project in projects:
        if project.id != target_project.id and project.boards:
            boards_by_project[project.name] = list(project.boards)
            total_boards += len(project.boards)
    
    if total_boards == 0:
        print(f"\n⚠ Нет досок для перемещения в '{target_project.name}'")
        return
    
    print(f"\n📊 Будет перемещено досок: {total_boards}")
    for proj_name, boards in boards_by_project.items():
        print(f"\n  Из проекта '{proj_name}' ({len(boards)} досок):")
        for board in boards:
            print(f"    - {board.name}")
    
    rename = input(f"\nДобавлять названия исходных проектов как префиксы? (y/n): ").strip().lower()
    use_prefix = rename == 'y'
    
    confirm = input(f"\nПереместить все {total_boards} досок в '{target_project.name}'? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("✗ Операция отменена")
        return
    
    success_count = 0
    error_count = 0
    
    print("\nПеремещение досок (копирование со всем содержимым):")
    
    for proj_name, boards in boards_by_project.items():
        prefix = proj_name if use_prefix else None
        print(f"\n  Из проекта '{proj_name}':")
        
        for board in boards:
            if move_board_with_content(planka, board, target_project, prefix, delete_source=True):
                new_name = f"{prefix} - {board.name}" if prefix else board.name
                print(f"    ✓ {board.name} → {new_name} (со всеми списками и карточками)")
                success_count += 1
            else:
                print(f"    ✗ {board.name}: Ошибка перемещения")
                error_count += 1
    
    print(f"\n{'='*60}")
    print("РЕЗУЛЬТАТЫ:")
    print(f"  Успешно перемещено: {success_count}")
    print(f"  Ошибок: {error_count}")
    print(f"{'='*60}")


def add_manager_to_all_projects(planka: PlankaClient, manager: object) -> None:
    """Добавляет менеджера ко всем проектам"""
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
            existing_managers = [m.id for m in project.managers]
            
            if manager.id in existing_managers:
                print(f"  ⊙ {project.name}: Уже является менеджером")
                skip_count += 1
            else:
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
    """Главная функция программы"""
    print(f"{'='*60}")
    print("УПРАВЛЕНИЕ ПРОЕКТАМИ И ДОСКАМИ PLANKA")
    print(f"{'='*60}")
    PLANKA_URL = os.getenv('PLANKA_URL', 'https://planka.mad-auto.ru/')
    
    API_KEY = os.getenv('PLANKA_API_KEY')
    
    if not API_KEY or API_KEY == 'your_api_key_here':
        print("API ключ не найден в .env файле или использует значение по умолчанию.")
        base_url = PLANKA_URL
        username = input("Введите имя пользователя или email: ").strip()
        password = input("Введите пароль: ").strip()
        
        print("\n⌛ Получение API токена...")
        
        api_token = get_api_token(base_url, username, password)
        
        if api_token:
            print(f"API Token (первые 20 символов): {api_token[:20]}...")
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
    
    try:
        planka = PlankaClient(PLANKA_URL, API_KEY)
        
        current_user = planka.me
        print(f"✓ Успешно подключено как: {current_user.name or current_user.username}")
        
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return
    
    while True:
        operation = select_operation()
        
        if operation == 'add_manager_all':
            manager = select_user(planka)
            
            if manager:
                add_manager_to_all_projects(planka, manager)
            else:
                print("\n✗ Операция отменена")
        
        elif operation == 'show_projects':
            display_projects(planka)
        
        elif operation == 'show_users':
            display_users(planka)
        
        elif operation == 'move_boards':
            move_boards_between_projects(planka)
        
        elif operation == 'consolidate_boards':
            consolidate_all_boards(planka)
        
        elif operation == 'exit':
            print("\n👋 До свидания!")
            break
        
        else:
            print("\n✗ Неверный выбор. Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
