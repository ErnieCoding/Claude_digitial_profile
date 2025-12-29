from MemoryTool import MemoryTool, SYSTEM_PROMPT, MODEL, BETAS
from ClaudeClient import Client

CREATE_ANALYTICS_DATABASE_PROMPT = """Ты - аналитик данных, который создаёт промежуточную базу данных для ускорения аналитических запросов.

## ЗАДАЧА:
Проанализируй ВСЕ файлы встреч в transcripts/ и создай сводный файл analytics_db.json с агрегированными данными.

## КРИТИЧЕСКИ ВАЖНО:
- Путь: /memories/analytics_db.json (С ведущим слешем!)
- Передай file_text с ПОЛНЫМ содержимым JSON
- НЕ создавай пустой файл

### Классификация статусов клиентов
✅ УСПЕШНЫЕ встречи (successful, клиент согласился на следующий шаг):
- в графе "meeting_success" стоит значение "да"

❌ НЕУСПЕШНЫЕ встречи (failed, клиент не согласился на следующий шаг):
- в графе "meeting_success" стоит значение "нет"

⏸️ НЕЙТРАЛЬНЫЕ встречи (neutral, решение ещё не принято)
- в графе "meeting_success" стоит значение "непонятно"

## СТРУКТУРА ФАЙЛА (<num>, "" И [] - ПЛЕЙСХОЛДЕРЫ, ВМЕСТО НИХ ПОСТАВЬ АКТУАЛЬНЫЕ ДАННЫЕ):

```json
{
  "metadata": {
    "total_meetings": <num>,
    "successful_meetings": {
      "count": <num>,
      "filenames": [],
      "meeting_ids": [],
    },
    "unsuccessful_meetings": {
      "count": <num>,
      "filenames": [],
      "meeting_ids": [],
    },
    "neutral_meetings": {
      "count": <num>,
      "filenames": [],
      "meeting_ids": [],
    },
    "overall_conversion": <num>,
    "last_updated": "",
    "meetings_date_range": {
      "start": "",
      "end": ""
    }
  },
  
  "conversion_by_month": {
    "Month-1": {
      "total": <num>,
      "successful": <num>,
      "conversion": <num>,
      "meetings_filenames": [],
      "meeting_ids": []
    },
    "Month-2": {
      "total": <num>,
      "successful": <num>,
      "conversion": <num>,
      "meetings_filenames": [],
      "meeting_ids": []
    },
    "Month-3": {
      "total": <num>,
      "successful": <num>,
      "conversion": <num>,
      "meetings_filenames": [],
      "meeting_ids": []
    }
  },
  
  "conversion_by_manager": {
    "Manager 1": {
      "total_meetings": <num>,
      "successful": <num>,
      "conversion": <num>,
      "average_activity": <num>,
      "meetings_filenames": [],
      "meeting_ids": []
    },
    "Manager 2": {
      "total_meetings": <num>,
      "successful": <num>,
      "conversion": <num>,
      "average_activity": <num>,
      "meetings_filenames": [],
      "meeting_ids": []
    }
  },
  
  "criteria_averages": {
    "successful_meetings": {
      "rapport_building": <num>,
      "situation_discovery": <num>,
      "problem_existence_depth": <num>,
      "problem_implications": <num>,
      "need_payoff_clarity": <num>,
      "sales_questioning_quality": <num>,
      "solution_fit": <num>,
      "client_engagement": <num>,
      "engagement_dynamics": <num>,
      "solution_presentation_quality": <num>,
      "understanding_validation": <num>,
      "objection_handling": <num>,
      "clear_next_steps": <num>,
      "stakeholder_mapping": <num>,
      "budget_timeline_qualification": <num>,
      "client_task_classification": <num>,
      "cognitive_overload_assessment": <num>
    },
    "failed_meetings": {
      "rapport_building": <num>,
      "situation_discovery": <num>,
      "problem_existence_depth": <num>,
      "problem_implications": <num>,
      "need_payoff_clarity": <num>,
      "sales_questioning_quality": <num>,
      "solution_fit": <num>,
      "client_engagement": <num>,
      "engagement_dynamics": <num>,
      "solution_presentation_quality": <num>,
      "understanding_validation": <num>,
      "objection_handling": <num>,
      "clear_next_steps": <num>,
      "stakeholder_mapping": <num>,
      "budget_timeline_qualification": <num>,
      "client_task_classification": <num>,
      "cognitive_overload_assessment": <num>
    },
    "neutral_meetings": {
      "rapport_building": <num>,
      "situation_discovery": <num>,
      "problem_existence_depth": <num>,
      "problem_implications": <num>,
      "need_payoff_clarity": <num>,
      "sales_questioning_quality": <num>,
      "solution_fit": <num>,
      "client_engagement": <num>,
      "engagement_dynamics": <num>,
      "solution_presentation_quality": <num>,
      "understanding_validation": <num>,
      "objection_handling": <num>,
      "clear_next_steps": <num>,
      "stakeholder_mapping": <num>,
      "budget_timeline_qualification": <num>,
      "client_task_classification": <num>,
      "cognitive_overload_assessment": <num>
    }
  }
}
```

## ИНСТРУКЦИИ:

1. **Прочитай ВСЕ JSON файлы из transcripts/**
2. **Агрегируй данные** по всем категориям выше
3. **Вычисли корреляции** между критериями и успехом
4. **Найди аномалии** (высокие оценки + провал, низкие оценки + успех)
5. **Создай индекс** с кратким описанием каждой встречи, включая названия встреч (файлов)
6. **Сохрани в memories/analytics_db.json**

## ВАЖНО:
- Используй точные математические вычисления (не округляй до целых)
- Если данных недостаточно для корреляции, укажи null
- Сохраняй список meetings_filenames вместе с meetings_ids по каждой встрече для быстрого доступа к детальным данным
"""

if __name__ == "__main__":
    client = Client()

    memory = MemoryTool()

    runner = client.client.beta.messages.tool_runner(
            betas=BETAS,
            model=MODEL,
            max_tokens=20000, # max_tokens для ответа
            system=SYSTEM_PROMPT,
            tools=[memory],
            messages=[
                {
                    "role":"user",
                    "content": CREATE_ANALYTICS_DATABASE_PROMPT,
                }
            ]
    )
    
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
