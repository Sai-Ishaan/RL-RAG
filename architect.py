import json

class Architect:
    def __init__(self, model_client):
        self.client = model_client

    def plan_architecture(self, vibe):
        prompt = f""" 
        You are a Lead React and React Native Architect for the given:
        Vibe:{vibe}
        Break this down into modular component structure.
        Return this Only in JSON Object format with the following:
        (i) 'components': Lost of objects with name as well as description
        (ii) 'data_flow': Flow that describes how components 'talk' to each other.
        (iii) 'complexity_estimate': An integer from 1-10.
    """
        
        response = self.client.chat.completions.create( ##Currently using ollama 
                model="llama3",
                messages=[
                    {"role": "system", "content":"You are a software architect"},
                    {"role": "user", "content":prompt}
                ],
                response_format={"type":"json_object"}
        )
        raw_text = response.choices[0].message.content
        try:
            plan = self.extract_json(raw_text)
            return plan
        except Exception as e:
            return {"error": "Invalid Blueprint", "raw": raw_text}
        
    def extract_json(self, text):
        start = text.find('{') # Using simple extraction for now
        end = text.rfind('}') + 1
        return json.loads(text[start:end])