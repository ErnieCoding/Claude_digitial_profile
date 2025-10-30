from MemoryTool import MemoryTool, MODEL, BETAS, SYSTEM_PROMPT


IDENTIFY_PARTICIPANTS_PROMPT = """Ты - передовая лингвистическая модель, способная распозновать людей из неструктрурированного текста-транскриптов бизнес встреч. Для этого ты проверяешь всю информацию из предоставленных встреч и создаешь полный список регулярных участников. 

КРИТИЧЕСКИ ВАЖНО:
1. Ты ДОЛЖЕН проанализировать ВСЕ файлы в директории /transcripts/
2. Каждый найденный участник должен быть учтен в конечном списке
3. НЕ ДУБЛИРУЙ УЧАСТНИКОВ. Добавляй каждого найденного участника только один раз.
4. ДОБАВЛЯЙ ТОЛЬКО АКТИВНЫХ УЧАСТНИКОВ ВСТРЕЧИ. Не добавляй имена, которые упоминаются коротко и без активного участия в транскриптах.
5. Список должен постоянно дополняться и обновляться при находке новых данных
6. НЕ ОСТАНАВЛИВАЙСЯ после анализа первого файла - продолжай до конца
7. В конце работы предоставь сводку: сколько файлов проверено, сколько участников было внесено в конечный

Твоя задача:
1. Изучи транскрипты из директории /transcripts/
2. Создай список участников встреч в директории /memories/ с названием participants.txt
3. Список должен содержать имена участников встречи (так, как они упоминаются в транскриптах)
4. Если список уже был создан, дополни его новыми данныии

Список участников должен быть сохранен в файле с названием participants.txt с каждым именем участника на новой строке.

Формат вывода:

Иван Иванов
Петр Петров
Артем Артемов
"""

class Identifier:
    def __init__(self, llm_client):
        self.client = llm_client
        self.memory = MemoryTool()
    
    def identify(self):
        print("\n==================[DEBUG] IDENTIFYING PARTICIPANTS==================\n")
        
        runner = self.client.beta.messages.tool_runner(
            betas=BETAS,
            model=MODEL,
            max_tokens=10000, # max_tokens для цифровых профилей
            system=SYSTEM_PROMPT,
            tools=[self.memory],
            messages=[
                {
                    "role":"user",
                    "content": IDENTIFY_PARTICIPANTS_PROMPT,
                }
            ]
        )

        print("\n==================[DEBUG] PARTICIPANTS IDENTIFIED==================\n")

        try:
            with open("memory/memories/participants.txt", "r") as f:
                lines = f.readlines()
            
            for line in lines:
                print(line + "\n")
        except FileNotFoundError as e:
            print(f"\n\n[ERROR] Error processing participants.txt: {e}")
            return