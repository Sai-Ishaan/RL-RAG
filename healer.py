class Healer:
    def __init__(self, builder):
        self.builder = builder

    def clean_code(self, code_string):
        if "```" in code_string:
            parts = code_string.split("```")
            for part in parts:
                if "import " in part or "const " in part:
                    code_string = part.replace("typescript", "").replace("tsx", "").strip()
                    break
        return code_string.strip() 

    def heal(self, comp_name, current_code, error_logs):
            ##Takes broken shitty code + compiler error and asks LLM to fix
            heal_prompt = f"Critical fix required for {comp_name}.tsx, \n The Error Logs are as follows: {error_logs} \n RULE: All UI Components like Viuew, Text, TouchableOpacity, Switch etc MUST be imported from 'react-native. They do Not exist in 'react'! \n Example Usage: import {{ View, Text. Switch }} from 'react-native \n\n Origina Code: {current_code}"
            raw_fixed_code = self.builder.generate_component(comp_name=comp_name,component_desc=heal_prompt,context_snippets="")
            return self.clean_code(raw_fixed_code)
