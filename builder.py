##builder.py uses a system prompt that instructs AI to write React Native Code.
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Builder:
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama") ##Ollama's local endpt
        self.model = "llama3"

    def generate_component(self, comp_name, component_desc, context_snippets=""):
        #Formatting RAG context into readable string
        memory_context = ""
        if context_snippets:
            memory_context = "\n Previous Verified Solutions(Use as Reference)...\n"
            for i, snippet in enumerate(context_snippets):
                #comp_name = snippet['blueprint']['components'][0]['name']
                code_sample = snippet.get('code', {}).get(comp_name, "// Code match not found")
                memory_context += f"Example{i+1} ({snippet['vibe']}):\n{code_sample[:500]}...\n"

        
        ##Generates React Natice component based on "vibe"
        system_message = (
            "You are a strict React-Native TSX generator. "
            "Output ONLY raw TypeScript code. NO markdown, NO explanations. "
            "Ensure all imports from 'react-native' are present."    
            )

        user_message = (
            f"TASK: Create a component named {comp_name}. \n"
            f"DESCRIPTION: {component_desc}\n"
            f"{memory_context}\n"
            f"Return ONLY the source code for {comp_name}.tsx"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role":"system", "content":system_message},
                    {"role":"user", "content": user_message}
                ],
                temperature=0.2 #Lower for code readability 
        )
            return response.choices[0].message.content.strip() #Grabs the first choice.
        except Exception as e:
            print(f"Builder Error: {e}")
            return f"//Error generating component {str(e)}"
## Quick test
# 
if __name__ == "__main__":
    builder = Builder()
    test_name = "LoginButton"
    test_desc = "A simple login button with a green background and white text"
    
    code = builder.generate_component(test_name, test_desc)
    print(f"Generated Code:{test_name}")
    print("-"*10)
    print(code)
    print("-"*10)
