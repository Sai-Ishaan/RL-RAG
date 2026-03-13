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

    def heal(self, broken_code, error_msg):
            ##Takes broken shitty code + compiler error and asks LLM to fix
            heal_prompt = (
                 f"The following React Native code failed to compile:\n\n"
                 f"CODE:\n{broken_code}\n\n"
                 f"ERROR:\n{error_msg}\n\n"
                 f"STRICT: Output ONLY raw Typescript. No backticks, no Talk."
            )
            raw_fixed_code = self.builder.generate_component("Fix this code", context_snippets=heal_prompt)
            return self.clean_code(raw_fixed_code)
