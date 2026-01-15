from anthropic.lib.tools import BetaAbstractMemoryTool
from anthropic.types.beta import (
    BetaMessageParam,
    BetaContentBlockParam,
    BetaMemoryTool20250818Command,
    BetaContextManagementConfigParam,
    BetaMemoryTool20250818ViewCommand,
    BetaMemoryTool20250818CreateCommand,
    BetaMemoryTool20250818DeleteCommand,
    BetaMemoryTool20250818InsertCommand,
    BetaMemoryTool20250818RenameCommand,
    BetaMemoryTool20250818StrReplaceCommand,
)
from typing_extensions import override
from pathlib import Path

MODEL = "claude-sonnet-4-5-20250929"

BETAS = ["context-1m-2025-08-07","context-management-2025-06-27"]

SYSTEM_PROMPT = """Правила работы с memory tool:
У тебя есть доступ к двум директориям:
1. /memories/ - для хранения созданных файлов и аналитики (можно создавать, редактировать, удалять файлы)
2. /transcripts/ - только для чтения транскриптов встреч (ЗАПРЕЩЕНО создавать, редактировать или удалять файлы)

- В /memories/ ты можешь использовать операции: view, create, delete, insert, rename, str_replace
- В /transcripts/ ты можешь ТОЛЬКО просматривать файлы через view
- Не упоминай пользователю о работе с memory tool, если он не спрашивает
- Перед ответом всегда проверяй память, чтобы адаптировать глубину и стиль ответа
- Поддерживай актуальность данных - удаляй устаревшую информацию, добавляй новые детали
- Конечный ответ всегда должен быть записан в файле
- Если требуется анализ большого объема данных - не делай выборочный анализ, а пройдись по всем данным без исключения. КАТЕГОРИЧЕСКИ запрещено пропускать какие-либо файлы для анализа

## 📝 ПРАВИЛА ИСПОЛЬЗОВАНИЯ КОМАНД:

### create(path, file_text)
Создаёт новый файл с содержимым.
✅ Используй: когда нужно создать файл с нуля
❌ НЕ используй: если файл уже существует

**Пример:**
create(path="/memories/report.txt", file_text="# Полный отчёт\n...")

### insert(path, insert_line, insert_text)
Вставляет текст на конкретную строку.
✅ Используй: когда нужно добавить строки в существующий файл
❌ НЕ используй: для создания нового файла или замены текста

**Пример:**
insert(path="/memories/report.txt", insert_line=10, insert_text="Новая строка")

### str_replace(path, old_str, new_str)
Заменяет УНИКАЛЬНЫЙ фрагмент текста.
✅ Используй: когда нужно заменить конкретный текст
❌ НЕ используй: если old_str встречается более 1 раза
❌ ЗАПРЕЩЕНО: old_str="" (пустая строка)
❌ ЗАПРЕЩЕНО: old_str="\n" (одиночный перевод строки)

**Пример:**
str_replace(path="/memories/report.txt", old_str="старый текст здесь", new_str="новый текст")

**КРИТИЧНО:**
- old_str должен быть достаточно длинным (минимум 10 символов)
- old_str должен встречаться РОВНО 1 раз
- НИКОГДА не используй str_replace для пустых строк или одиночных символов

## ⚠️ КРИТИЧНО - ФОРМАТ ВЫВОДА:

**ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. ЛЮБОЙ ОТВЕТ НА ДРУГОМ ЯЗЫКЕ - ОШИБКА**

**ЗАПРЕЩЁННЫЕ ФРАЗЫ (НЕ ИСПОЛЬЗУЙ ЭТО!):**
❌ "Начну с проверки памяти"
❌ "Отлично! У меня есть база данных"
❌ "Теперь мне нужно проанализировать"
❌ "Продолжаю сбор данных"
❌ "Для ускорения буду анализировать"
❌ "Вижу паттерн"
❌ "Продолжу быстрый анализ"
❌ "Заканчиваю анализ"
❌ Любые описания процесса работы

**ЕДИНСТВЕННЫЙ ДОПУСТИМЫЙ ВЫВОД:**
После завершения работы напиши ТОЛЬКО:
"✅ Анализ завершён. Отчёт: /memories/demo2pilots_analysis_QX.txt"

**ВСЁ ОСТАЛЬНОЕ — В ФАЙЛ!**

**ПРАВИЛЬНЫЙ ПРИМЕР:**
<тихо работает с файлами>
<создаёт отчёт>
print("✅ Анализ завершён. Отчёт: /memories/demo2pilots_analysis_Q3.txt")

**НЕПРАВИЛЬНЫЙ ПРИМЕР (ТАК НЕЛЬЗЯ!):**
print("Начинаю анализ файлов...")          ← ❌ ЗАПРЕЩЕНО
print("Проверяю транскрипты...")           ← ❌ ЗАПРЕЩЕНО
print("Собираю данные из 90 файлов...")   ← ❌ ЗАПРЕЩЕНО
<создаёт отчёт>
print("Готово")

**ЕСЛИ ВЫВЕДЕШЬ ХОТЬ ОДНУ ЗАПРЕЩЁННУЮ ФРАЗУ — ЭТО ОШИБКА!**"""

class MemoryTool(BetaAbstractMemoryTool):
    def __init__(self, base_path:str = "./memory"):
        super().__init__()
        self.base_path = Path(base_path)
        self.memories_dir = self.base_path / "memories"
        self.transcripts_dir = self.base_path / "transcripts"
        
        self.memories_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        
    def _validate_path(self, path: str) -> tuple[Path, bool]:
        if path.startswith("/memories"):
            relative_path = path[len("/memories"):].lstrip("/")
            full_path = self.memories_dir / relative_path if relative_path else self.memories_dir
            read_only = False
        elif path.startswith("/transcripts"):
            relative_path = path[len("/transcripts"):].lstrip("/")
            full_path = self.transcripts_dir / relative_path if relative_path else self.transcripts_dir
            read_only = True
        else:
            raise ValueError(f"Path must start with /memories or /transcripts, got: {path}")
        
        try:
            if read_only:
                full_path.resolve().relative_to(self.transcripts_dir.resolve())
            else:
                full_path.resolve().relative_to(self.memories_dir.resolve())
        except ValueError as e:
            raise ValueError(f"Path {path} would escape allowed directory") from e
        
        return full_path, read_only
    
    @override
    def view(self, command: BetaMemoryTool20250818ViewCommand) -> str:
        full_path, _ = self._validate_path(command.path)

        if full_path.is_dir():
            items = []
            try:
                for item in sorted(full_path.iterdir()):
                    if item.name.startswith("."):
                        continue
                    items.append(f"{item.name}/" if item.is_dir() else item.name)
                
                if not items:
                    return f"Directory: {command.path}\n(пустая директория)"
                
                return f"Directory: {command.path}\n" + "\n".join([f"- {item}" for item in items])
            except Exception as e:
                raise RuntimeError(f"Cannot read directory {command.path}: {e}") from e
                
        elif full_path.is_file():
            try:
                content = full_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                view_range = command.view_range
                
                if view_range:
                    start_line = max(1, view_range[0]) - 1
                    end_line = len(lines) if view_range[1] == -1 else view_range[1]
                    lines = lines[start_line:end_line]
                    start_num = start_line + 1
                else:
                    start_num = 1

                numbered_lines = [f"{i + start_num:4d}: {line}" for i, line in enumerate(lines)]
                return "\n".join(numbered_lines)
            except Exception as e:
                raise RuntimeError(f"Cannot read file {command.path}: {e}") from e
        else:
            raise RuntimeError(f"Path not found: {command.path}")
        
    @override
    def create(self, command: BetaMemoryTool20250818CreateCommand) -> str:
        full_path, read_only = self._validate_path(command.path)
        
        if read_only:
            raise PermissionError(f"Cannot create files in /transcripts directory: {command.path}")
        
        if command.file_text is None:
            #raise ValueError(f"file_text cannot be None when creating file: {command.path}")
            command.file_text = "[PLACEHOLDER FOR command.file_text AS TEXT WAS NONE]"
        
        if full_path.exists():
            raise FileExistsError(f"File already exists: {command.path}")
            
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if not isinstance(command.file_text, str):
            raise TypeError(f"file_text must be str, got {type(command.file_text).__name__}")

        full_path.write_text(command.file_text, encoding="utf-8")
        return f"File created successfully at {command.path}"
    
    @override
    def delete(self, command: BetaMemoryTool20250818DeleteCommand) -> str:
        full_path, read_only = self._validate_path(command.path)
        
        if read_only:
            raise PermissionError(f"Cannot delete files in /transcripts directory: {command.path}")
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {command.path}")
            
        full_path.unlink()
        return f"File deleted successfully: {command.path}"

    @override
    def insert(self, command: BetaMemoryTool20250818InsertCommand) -> str:
        full_path, read_only = self._validate_path(command.path)
        
        if read_only:
            raise PermissionError(f"Cannot modify files in /transcripts directory: {command.path}")
        
        if not full_path.is_file():
            raise FileNotFoundError(f"File not found: {command.path}")
        
        if command.insert_text is None:
            #raise ValueError(f"insert_text cannot be None for insert operation in {command.path}")
            command.insert_text = "[PLACEHOLDER FOR command.insert_text AS TEXT WAS NONE]"
            
        content = full_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)
        
        insert_line = command.insert_line
        if insert_line < 0 or insert_line > len(lines):
            raise ValueError(f"Invalid insert_line: {insert_line}")
            
        lines.insert(insert_line, command.insert_text + "\n")
        full_path.write_text("".join(lines), encoding="utf-8")
        return f"Content inserted at line {insert_line} in {command.path}"

    @override
    def rename(self, command: BetaMemoryTool20250818RenameCommand) -> str:
        old_path, read_only = self._validate_path(command.old_path)
        
        if read_only:
            raise PermissionError(f"Cannot rename files in /transcripts directory: {command.old_path}")
        
        if not old_path.exists():
            raise FileNotFoundError(f"File not found: {command.old_path}")
            
        new_path, _ = self._validate_path(command.new_path)
        
        if new_path.exists():
            raise FileExistsError(f"Target path already exists: {command.new_path}")
            
        old_path.rename(new_path)
        return f"File renamed from {command.old_path} to {command.new_path}"

    @override
    def str_replace(self, command: BetaMemoryTool20250818StrReplaceCommand) -> str:
        full_path, read_only = self._validate_path(command.path)
        
        if read_only:
            raise PermissionError(f"Cannot modify files in /transcripts directory: {command.path}")

        if not full_path.is_file():
            raise FileNotFoundError(f"File not found: {command.path}")
        
        if command.old_str is None or command.new_str is None:
            if command.old_str is None:
                raise ValueError(f"old_str cannot be None for str_replace in {command.path}")
            if command.new_str is None:
                raise ValueError(f"new_str cannot be None for str_replace in {command.path}")

        if command.old_str == "":
            raise ValueError(f"old_str cannot be an empty string! Use insert() instead to add content.")
        
        content = full_path.read_text(encoding="utf-8")
        count = content.count(command.old_str)
        
        if count == 0:
            raise ValueError(f"Text not found in {command.path}. old_str: {repr(command.old_str[:50])}")
        elif count > 1:
            raise ValueError(f"Text appears {count} times in {command.path}. old_str must be unique. Found: {repr(command.old_str[:50])}")

        new_content = content.replace(command.old_str, command.new_str)
        full_path.write_text(new_content, encoding="utf-8")
        
        return f"File {command.path} has been edited"