##builder.py uses a system prompt that instructs AI to write React Native Code.
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Builder:
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama") ##Ollama's local endpt
        self.model = "llama3"

    def generate_component(self, vibe_prompt: str, context_snippets=""):
        ##Generates React Natice component based on "vibe"
        system_message = (
    "You are a strict code generator. "
    "Output ONLY raw TypeScript code. "
    "NO markdown code blocks (no ```). "
    "NO explanations. "
    "Ensure all components (FlatList, View, Text, TouchableOpacity, useState) are imported from 'react' or 'react-native'."
    )

        user_message = f"Vibe: {vibe_prompt}\n\nContext from RAG:{context_snippets}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role":"system", "content":system_message},
                {"role":"user", "content": user_message}
            ],
            temperature=0.7 #High temp for 'vibe' intact hehe
        )

        return response.choices[0].message.content.strip()
    
## Quick test
# 
if __name__ == "__main__":
    builder = Builder()
    code = builder.generate_component("A simple login button with green background")
    print("Generated Code:")
    print(code)