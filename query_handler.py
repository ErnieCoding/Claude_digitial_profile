from MemoryTool import MemoryTool, SYSTEM_PROMPT, MODEL, BETAS
from ClaudeClient import Client

PROMPT = """Какое разивите динамики у сотрудника Елена? Ты должен указать динамику изменения его поведения и качеств таких как личная ответственность, лидерство, психологическая устойчивость и планирвоание и организация."""

if __name__ == "__main__":
    client = Client()

    memory = MemoryTool()

    runner = client.client.beta.messages.tool_runner(
            betas=BETAS,
            model=MODEL,
            max_tokens=1000, # max_tokens для ответа
            system=SYSTEM_PROMPT,
            tools=[memory],
            messages=[
                {
                    "role":"user",
                    "content":PROMPT,
                }
            ]
    )
    
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)