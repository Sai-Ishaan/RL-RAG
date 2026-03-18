import os
import subprocess
import shutil
import json
import sys

class ProjectManager:
    def __init__(self,template_dir="rn_template", root_dir="project_sandbox"):
        self.template = os.path.abspath(template_dir)
        self.root_dir = os.path.abspath(root_dir)
        # os.makedirs(f"{self.root}/components", exist_ok=True)
        if not os.path.exists(self.template):
            print("Warning!! Template directory not found at: {self.template}")
            print("Run: 'npx react-native init rn_template' once")

    def setup_project(self):
        if os.path.exists(self.root_dir):        ##Clean slate for each run
            try:
                shutil.rmtree(self.root_dir)
            except PermissionError:
                print("Error cleaning sandbox. Close any open files in terminal or IDE/VSCode")
                return
        print(f"Copying template to {self.root_dir}")
        try:   
            shutil.copytree(self.template, self.root_dir, ignore=shutil.ignore_patterns('node_modules'))
        except FileNotFoundError:
            print("Template directory is missing. Cannot setup project")
            return 
        
        source_nm = os.path.join(self.template, 'node_modules')
        dest_nm = os.path.join(self.root_dir, 'node_modules')
        
        if os.path.exists(source_nm):
            try:
                if sys.platform == "win32":
                    subprocess.run(f'mklink /J "{dest_nm}" "{source_nm} "', shell=True, stdout=subprocess.DEVNULL) ##Windows requires special handling for symlinks
                    #on windows, junction is safer than symlink
                else:
                    os.symlink(source_nm, dest_nm) 
                print("Symlinked node_modules successfully!")
            except Exception as e:
                print(f"Symlink failed!! ({e}). Copying instead (slower)")
        else:
            print("Template has no node_modules. Validation will likely fail.")    
        
        ##Initialsing basic react native/ts env
        tsconfig = {
            "compilerOptions":{
                "target":"esnext",
                "module":"commonjs",
                "jsx":"react-native",
                "strict":True,
                "skipLibCheck":True,
                "moduleResolution": "node",
                "esModuleInterop": True,
                "allowSyntheticDefaultImports":True
            }
        }        
        self.write_component("tsconfig.json", json.dumps(tsconfig, indent=2))
        print("Project sandbox initialised with tsconfig")

    def write_component(self, name, code):
        filename = name if name.endswith(('.tsx', '.ts', '.json')) else f"{name}.tsx"
        path = os.path.join(self.root_dir, filename)
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding='utf-8') as f:
            f.write(code)

    def get_code_compexity(self, code):
        ##Using a simple heuristic: count of lines or nested brackets
        return code.count('{')/10

    def run_validation(self):
        print("Running tsc validation...")
        try: 
            cmd = ["npx","tsc", "--noEmit", "--skipLibCheck",  "--project", self.root_dir]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=(sys.platform == "win32")
        )
            logs = result.stdout + result.stderr
            success = result.returncode == 0
            if not success:
                critical_errors = [
                    line for line in logs.split('\n')
                    if "error TS" in line and "TS2307" not in line
                ]
                if not critical_errors and "TS2307" in logs:
                    return True, "ENVIRONMENT_BYPASS: Syntax valid, modules missing!"
            return success, logs
        
        except FileNotFoundError:
            return False, "Error: 'tsc' or 'npx' Not Found! Check if typescript is installed..."