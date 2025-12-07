import os
from pathlib import Path
import json

def fix_filename_encoding(name: str) -> str:
    try:
        raw_bytes = name.encode('latin-1')

        fixed = raw_bytes.decode('utf-8')

        return fixed
    except:
        return name

def rename_broken_filenames(directory="memory/transcripts"):
    directory = Path(directory)

    if not directory.exists():
        print(f"Директория {directory} не существует")
        return

    json_files = list(directory.glob("*.json"))
    if not json_files:
        print(f"В {directory} нет json-файлов")
        return

    renamed = 0

    print("\nПереименование файлов:\n")

    for file_path in json_files:
        broken_name = file_path.stem                      # имя без .json
        fixed_name = fix_filename_encoding(broken_name)   # исправленное имя

        # Если имя уже нормальное — пропускаем
        if broken_name == fixed_name:
            print(f"✓ {file_path.name} (уже нормально)")
            continue

        new_path = file_path.with_name(f"{fixed_name}.json")

        try:
            file_path.rename(new_path)
            print(f"→ {file_path.name}")
            print(f"     {fixed_name}.json\n")
            renamed += 1
        except Exception as e:
            print(f"!! Ошибка при переименовании {file_path.name}: {e}")

    print("\n==============================")
    print(f"Готово. Переименовано: {renamed}")
    print("==============================")


def convert_txt_to_json(directory="memory/transcripts"):
    """
    1. Исправляет кодировку имён файлов
    2. Конвертирует .txt в .json
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Директория {directory} не найдена!")
        return
    
    renamed_count = 0
    converted_count = 0
    errors = []
    
    txt_files = list(directory.glob("*.txt"))
    
    if not txt_files:
        print(f"В директории {directory} нет .txt файлов")
        return
    
    print(f"Найдено файлов: {len(txt_files)}\n")
    
    for file_path in txt_files:
        original_name = file_path.name
        
        try:
            # Шаг 1: Исправляем кодировку имени
            name_without_ext = file_path.stem
            extension = file_path.suffix
            
            fixed_name = fix_filename_encoding(name_without_ext)
            
            # Шаг 2: Меняем расширение на .json
            new_name = f"{fixed_name}.json"
            new_path = file_path.parent / new_name
            
            # Шаг 3: Проверяем, что содержимое - валидный JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Удаляем markdown-обёртку ```json ... ```
                    if content.strip().startswith('```json'):
                        content = content.strip()
                        content = content.replace('```json', '', 1)
                        content = content.rsplit('```', 1)[0]
                        content = content.strip()
                    
                    # Валидируем JSON
                    json_data = json.loads(content)
                
                # Шаг 4: Записываем в новый файл с правильным именем
                with open(new_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                # Шаг 5: Удаляем старый файл
                file_path.unlink()
                
                print(f"✅ {original_name}")
                print(f"   → {new_name}\n")
                
                converted_count += 1
                if original_name != new_name:
                    renamed_count += 1
                    
            except json.JSONDecodeError as e:
                errors.append(f"{original_name}: Невалидный JSON - {e}")
                print(f"❌ {original_name}: JSON ошибка")
                
        except Exception as e:
            errors.append(f"{original_name}: {e}")
            print(f"❌ {original_name}: Ошибка - {e}")
    
    # Итоги
    print(f"\n{'='*60}")
    print(f"📊 ИТОГИ:")
    print(f"{'='*60}")
    print(f"✅ Конвертировано: {converted_count} файлов")
    print(f"🔤 Переименовано: {renamed_count} файлов")
    
    if errors:
        print(f"\n⚠️ Ошибки ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")


def preview_filenames(directory="memory/transcripts"):
    """
    Показывает, как изменятся имена .json файлов.
    """
    directory = Path(directory)

    if not directory.exists():
        print(f"❌ Директория {directory} не найдена!")
        return

    json_files = list(directory.glob("*.json"))
    if not json_files:
        print(f"⚠️ В директории {directory} нет .json файлов")
        return

    print("📋 ПРЕДПРОСМОТР ИСПРАВЛЕНИЯ ИМЁН\n")
    print(f"{'БЫЛО':<50} → {'СТАНЕТ':<50}")
    print(f"{'-'*50} → {'-'*50}")

    for file_path in json_files:
        original = file_path.name
        fixed_stem = fix_filename_encoding(file_path.stem)
        new_name = f"{fixed_stem}.json"
        print(f"{original:<50} → {new_name:<50}")


if __name__ == "__main__":
    import sys
    
    print("🔧 Исправление кодировки и конвертация в JSON\n")
    
    preview_filenames()
    print(f"\n{'='*60}")
    response = input("Выполнить конвертацию? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y', 'да', 'д']:
        print("\nНачинаем конвертацию...\n")
        convert_txt_to_json()
    else:
        print("Отменено пользователем")