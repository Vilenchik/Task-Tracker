import json
import argparse
from datetime import datetime
from pathlib import Path

TASKS_FILE = 'tasks.json'

def load_tasks():
    """Загружает задачи из файла, гарантируя что ключи будут целыми числами"""
    try:
        with open(TASKS_FILE, 'r') as f:
            data = json.load(f)
            # Преобразуем ключи в int на случай если они сохранились как строки
            return {int(k): v for k, v in data.items()} if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файла нет или он поврежден, создаем новый
        Path(TASKS_FILE).touch()
        with open(TASKS_FILE, 'w') as f:
            json.dump({}, f)
        return {}

def save_tasks(tasks):
    """Сохраняет задачи в файл с красивым форматированием"""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def validate_task_id(tasks, task_id):
    """Проверяет существование задачи и возвращает её"""
    if task_id not in tasks:
        print(f"Error: Task ID {task_id} not found")
        return None
    return tasks[task_id]

def add_task(tasks, args):
    """Добавляет новую задачу"""
    if not args.add or not args.add.strip():
        print("Error: Task description cannot be empty")
        return
    
    task_id = max(tasks.keys(), default=0) + 1
    tasks[task_id] = {
        'text': args.add.strip(),
        'status': 'not_done',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    print(f"Task added with ID {task_id}")

def update_task(tasks, args):
    """Обновляет описание задачи"""
    if args.update is None:
        print("Error: Task ID required")
        return
    
    task = validate_task_id(tasks, args.update)
    if not task:
        return
    
    new_text = input("Enter new task description: ").strip()
    if not new_text:
        print("Error: Description cannot be empty")
        return
    
    task['text'] = new_text
    task['updated_at'] = datetime.now().isoformat()
    print(f"Task {args.update} updated")

def delete_task(tasks, args):
    """Удаляет задачу"""
    if args.delete is None:
        print("Error: Task ID required")
        return
    
    if args.delete not in tasks:
        print(f"Error: Task ID {args.delete} not found")
        return
    
    del tasks[args.delete]
    print(f"Task {args.delete} deleted")

def change_task_status(tasks, task_id, new_status):
    """Общая функция для изменения статуса задачи"""
    task = validate_task_id(tasks, task_id)
    if not task:
        return False
    
    task['status'] = new_status
    task['updated_at'] = datetime.now().isoformat()
    print(f"Task {task_id} marked as {new_status}")
    return True

def markdone(tasks, args):
    """Помечает задачу как выполненную"""
    if args.markdone is None:
        print("Error: Task ID required")
        return
    change_task_status(tasks, args.markdone, 'done')

def markinprogress(tasks, args):
    """Помечает задачу как находящуюся в работе"""
    if args.markinprogress is None:
        print("Error: Task ID required")
        return
    change_task_status(tasks, args.markinprogress, 'in_progress')

def print_tasks(tasks, status_filter=None):
    """Выводит задачи с фильтром по статусу"""
    if not tasks:
        print("No tasks found")
        return
    
    title = "All Tasks" if status_filter is None else f"{status_filter.capitalize()} Tasks"
    print(f"\n{title}:")
    print("-" * 30)
    
    for task_id, task in tasks.items():
        if status_filter is None or task['status'] == status_filter:
            print(f"ID: {task_id}")
            print(f"Text: {task['text']}")
            print(f"Status: {task['status']}")
            print(f"Created: {task['created_at']}")
            if 'updated_at' in task:
                print(f"Updated: {task['updated_at']}")
            print("-" * 30)

def listdone(tasks, args):
    """Выводит выполненные задачи"""
    print_tasks(tasks, 'done')

def listinprogress(tasks, args):
    """Выводит задачи в работе"""
    print_tasks(tasks, 'in_progress')

def listnotdone(tasks, args):
    """Выводит невыполненные задачи"""
    print_tasks(tasks, 'not_done')

# Словарь обработчиков команд
handlers = {
    'add': add_task,
    'update': update_task,
    'delete': delete_task,
    'markdone': markdone,
    'markinprogress': markinprogress,
    'listdone': listdone,
    'listinprogress': listinprogress,
    'listnotdone': listnotdone
}

def main():
    """Основная функция, обрабатывающая аргументы командной строки"""
    parser = argparse.ArgumentParser(description='Task Tracker')
    
    # Аргументы командной строки
    parser.add_argument('-a', '--add', help='Add new task')
    parser.add_argument('-u', '--update', type=int, help='Update task (ID required)')
    parser.add_argument('-d', '--delete', type=int, help='Delete task (ID required)')
    parser.add_argument('-md', '--markdone', type=int, help='Mark task as done (ID required)')
    parser.add_argument('-mp', '--markinprogress', type=int, help='Mark task in progress (ID required)')
    parser.add_argument('-ld', '--listdone', action='store_true', help='List completed tasks')
    parser.add_argument('-lp', '--listinprogress', action='store_true', help='List in-progress tasks')
    parser.add_argument('-lnd', '--listnotdone', action='store_true', help='List pending tasks')

    args = parser.parse_args()
    tasks = load_tasks()
    
    # Обработка команд
    handled = False
    for arg_name, handler in handlers.items():
        arg_value = getattr(args, arg_name, None)
        # Для списковых команд (action='store_true') проверяем True/False
        if (arg_name in ['listdone', 'listinprogress', 'listnotdone'] and arg_value) \
           or (arg_name not in ['listdone', 'listinprogress', 'listnotdone'] and arg_value is not None):
            handler(tasks, args)
            if arg_name not in ['listdone', 'listinprogress', 'listnotdone']:
                save_tasks(tasks)
            handled = True
            break
    
    # Если ни одна команда не была выполнена, показать справку
    if not handled:
        parser.print_help()

if __name__ == '__main__':
    main()