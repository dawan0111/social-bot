import openai

class OpenAI:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

        openai.api_key = self.api_key
    
    def run(self, chats) -> str:
        print(chats)
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=chats
        )
        answer = response['choices'][0]['message']['content'].strip()

        return answer
    
if __name__ == "__main__":
    api_key = input("input your api key: ")
    model = input("input model name: ")
    question = input("무엇을 물어보실 껀가요? ")
    
    openAI = OpenAI(api_key, model)
    openAI.run(question)