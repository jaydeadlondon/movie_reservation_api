"""
Скрипт для запуска тестов Movie Reservation API
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    print("🎬 Movie Reservation API - Запуск тестов")
    print("=" * 60)

    if not Path("app").exists() or not Path("tests").exists():
        print("❌ Ошибка: Запустите скрипт из корневой директории проекта")
        sys.exit(1)

    print("📦 Проверка зависимостей...")
    try:
        import pytest
        import httpx

        print("✅ Зависимости установлены")
    except ImportError as e:
        print(f"❌ Не установлены зависимости: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        sys.exit(1)

    commands = [
        ("pytest --version", "Проверка версии pytest"),
        ("pytest -v --tb=short", "Запуск всех тестов"),
        ("pytest --cov=app --cov-report=term-missing", "Запуск с покрытием кода"),
    ]

    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
            break

    if success:
        print(f"\n{'='*60}")
        print("✅ Все тесты выполнены успешно!")
        print("📊 Отчет о покрытии кода создан")
        print("🎉 Готово!")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ Некоторые тесты не прошли")
        print("🔍 Проверьте вывод выше для деталей")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()
