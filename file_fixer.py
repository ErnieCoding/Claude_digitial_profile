import os
from pathlib import Path
import unicodedata

def fix_filename_encoding(directory = "memory/transcripts"):
    """
    Нормализует имена файлов из NFD в NFC
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Директория {directory} не найдена!")
        return
    
    renamed_count = 0
    
    print("Нормализация имён файлов в NFC...\n")
    
    # Получаем ВСЕ файлы (включая NFD)
    for file_path in directory.iterdir():
        if not file_path.is_file():
            continue
        
        original_name = file_path.name
        
        # Нормализуем в NFC
        nfc_name = unicodedata.normalize('NFC', original_name)
        
        if original_name != nfc_name:
            new_path = file_path.parent / nfc_name
            
            # Проверяем что файл с таким именем не существует
            if new_path.exists():
                print(f"⚠️  Пропущен (файл уже существует): {original_name}")
                continue
            
            # Переименовываем
            file_path.rename(new_path)
            
            print(f"✅ Переименован:")
            print(f"   Было (NFD): {repr(original_name[:50])}")
            print(f"   Стало (NFC): {repr(nfc_name[:50])}\n")
            
            renamed_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Переименовано файлов: {renamed_count}")
    print(f"{'='*60}")


def convert_txt_to_json_safe(directory="memory/transcripts"):
    """
    БЕЗОПАСНАЯ конвертация .txt в .json БЕЗ изменения содержимого
    
    Что делает:
    1. Исправляет кодировку имён файлов (если нужно)
    2. Меняет расширение .txt на .json
    3. Удаляет markdown обёртку ```json...``` (если есть)
    4. НЕ ТРОГАЕТ остальное содержимое (порядок ключей, форматирование, Unicode)
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Директория {directory} не найдена!")
        return
    
    txt_files = list(directory.glob("*.txt"))
    
    if not txt_files:
        print(f"В директории {directory} нет .txt файлов")
        return
    
    print(f"Найдено файлов: {len(txt_files)}\n")
    
    renamed_count = 0
    converted_count = 0
    errors = []
    
    for file_path in txt_files:
        original_name = file_path.name
        
        try:
            # Шаг 1: Читаем содержимое КАК ЕСТЬ (без парсинга!)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Шаг 2: Убираем ТОЛЬКО markdown обёртку (если есть)
            original_content = content
            content_stripped = content.strip()
            
            if content_stripped.startswith('```json') and content_stripped.endswith('```'):
                # Удаляем ```json в начале
                content = content_stripped[len('```json'):].strip()
                # Удаляем ``` в конце
                if content.endswith('```'):
                    content = content[:-3].strip()
                print(f"  🔧 Удалена markdown обёртка")
            elif content_stripped.startswith('```') and content_stripped.endswith('```'):
                # Обобщённый случай: ```...```
                content = content_stripped[3:-3].strip()
                print(f"  🔧 Удалена markdown обёртка")
            else:
                # Содержимое уже чистое
                content = original_content
            
            # Шаг 3: Исправляем имя файла (если нужно)
            name_without_ext = file_path.stem
            
            # Шаг 4: Создаём новый путь с расширением .json
            new_name = f"{name_without_ext}.json"
            new_path = file_path.parent / new_name
            
            # Шаг 5: Записываем содержимое БЕЗ ИЗМЕНЕНИЙ
            with open(new_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            
            # Шаг 6: Удаляем старый .txt файл
            file_path.unlink()
            
            print(f"✅ {original_name}")
            if original_name != new_name:
                print(f"   → {new_name}")
                renamed_count += 1
            
            converted_count += 1
            
        except Exception as e:
            errors.append(f"{original_name}: {e}")
            print(f"❌ {original_name}: {e}")
    
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

#TODO: Adjust this to fit new fix_filename_encoding
# def preview_conversion(directory="memory/transcripts"):
#     """
#     Показывает предпросмотр изменений БЕЗ применения
#     """
#     directory = Path(directory)
    
#     if not directory.exists():
#         print(f"❌ Директория {directory} не найдена!")
#         return
    
#     txt_files = list(directory.glob("*.txt"))
    
#     if not txt_files:
#         print(f"⚠️ В директории {directory} нет .txt файлов")
#         return
    
#     print("📋 ПРЕДПРОСМОТР КОНВЕРТАЦИИ\n")
#     print(f"{'БЫЛО':<60} → {'СТАНЕТ':<60}")
#     print(f"{'-'*60} → {'-'*60}")
    
#     for file_path in txt_files:
#         original = file_path.name
#         fixed_stem = fix_filename_encoding(file_path.stem)
#         new_name = f"{fixed_stem}.json"
        
#         # Проверяем, есть ли markdown обёртка
#         with open(file_path, 'r', encoding='utf-8') as f:
#             content = f.read().strip()
        
#         has_wrapper = content.startswith('```json') or content.startswith('```')
#         wrapper_note = " [+удалить обёртку]" if has_wrapper else ""
        
#         print(f"{original:<60} → {new_name:<60}{wrapper_note}")


if __name__ == "__main__":
    print(f"\n{'='*60}")
    response = input("Выполнить конвертацию? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y', 'да', 'д']:
        print("\nНачинаем конвертацию...\n")
        convert_txt_to_json_safe()
        fix_filename_encoding()
    else:
        print("❌ Отменено пользователем")