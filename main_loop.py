##main loop contains all builder, healer and evaluator
from builder import Builder
from evaluator import Evaluator
from healer import Healer
import time
import itertools
import re
from architect import Architect
#from prober import Prober
import json
from project_manager import ProjectManager
from vector_store import VectorStore
import os
import random
from datetime import datetime
from prober import inject_code

class TaskProber:
    def __init__(self):
        self.components = [
        "login screen", "user profile", "settings dashboard", "music player", 
            "weather widget", "e-commerce product card", "chat interface", 
            "notification feed", "calendar view", "analytics chart", 
            "image gallery", "task list", "checkout form", "sidebar navigation"
        ]
        self.styles = [
            "minimalist", "dark mode", "glassmorphism", "neuromorphic", 
            "flat design", "retro 80s", "high contrast", "corporate clean"
        ]

        self.constraints = [
            "with large typography", "using a red and black palette", 
            "with rounded corners", "with dense information density",
            "optimized for mobile", "with transparency effects"
        ]

    def generate_batch(self, count=100):
        all_combos = list(itertools.product(self.styles, self.components, self.constraints))
        random.shuffle(all_combos)

        batch = []
        for i, (style, comp, constraint) in enumerate(all_combos[:count]):
            prompt = f"Create a {style} {comp} {constraint}."
            batch.append(prompt)
        print(f"Generated {len(batch)} unique synthetic tasks.")
        return batch
    
class RLOrchestrator:
    def __init__(self):
        self.builder = Builder()
        self.evaluator = Evaluator()
        self.healer = Healer(self.builder)
        self.architect = Architect(self.builder.client)
        self.pm = ProjectManager()
        #self.prober = Prober()
        self.vs = VectorStore() ##For RAG context retrieval, not implemented in this snippet
    
    def calculate_composite_reward(self,success, logs, plan):
            if "ENVIRONMENT_BYPASS" in logs:
                return 0.6
            
            if not success:
                if "STRICT_MODE_BYPASS" in logs:
                    return 0.5
                return 0.0
            
            base = 1.0
            ## Extract complexity from architect's plan(if missing, default is 5)
            complexity = plan.get('complexity_estimate', 5)
            complexity_penalty = complexity * 0.02
            
            err_count = logs.lower().count('error')
            warn_count = logs.lower().count('warning')
            linter_penalty = (warn_count*0.05) + (err_count*0.1)
            ##Count occurences of error or warning in tsc logs
            return round(max(0.1, base- complexity_penalty - linter_penalty), 2)
    
    def assemble_sandbox_app(self, code_map):
        full_source = "import React, { useState, useEffect, useRef } from 'react';\n"
        full_source += "import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput, Image, SafeAreaView, FlatList, Switch, Dimensions } from 'react-native';\n"
        full_source += "import { LinearGradient } from 'expo-linear-gradient';\n"
        full_source += "import { Ionicons } from '@expo/vector-icons';\n\n"

        component_names = []
        for name, code in code_map.items():
            clean_code = re.sub(r"import .*?;", "", code) ##clean imports and exports for single file compatability
            clean_code = clean_code.replace("export default function", "function")
            clean_code = clean_code.replace("export default class", "class")
            full_source += f"// --- Component: {name} --\n {clean_code}\n\n"
            component_names.append(name)
        
        full_source += "\n// --Sandbox entry -- \n"
        full_source += "export default function GeneratedApp() {\n"
        full_source += "  return (\n"
        full_source += "    <SafeAreaView style={{ flex: 1, backgroundColor: '#1a1a1a' }}>\n"
        full_source += "      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 100 }}>\n"
        full_source += "        <Text style={{color: '#666', textAlign:'center', marginBottom: 20}}>Synthetic Training Monitor</Text>\n"

        for name in component_names:
            full_source += f"        <View style={{ marginBottom: 30, borderWidth: 1, borderColor: '#333', borderRadius: 12, overflow: 'hidden', backgroundColor: '#000' }}>\n"
            full_source += f"          <View style={{backgroundColor:'#222', padding:5}}><Text style={{color: '#888', fontSize: 10}}>{name}</Text></View>\n"
            full_source += f"          <View style={{padding: 10}}><{name} /></View>\n"
            full_source += f"        </View>\n"

        full_source += "      </ScrollView>\n"
        full_source += "    </SafeAreaView>\n"
        full_source += "  );\n"
        full_source += "}\n"

        return full_source

    def run_episode(self, vibe, episode_id, max_retries=2):
        ###Executes every single RL episode for a given prompt or vibe
        print(f"\n --- [New Episode#{episode_id}] Goal:{vibe} --- ")
        start_time = time.time()

        plan = self.architect.plan_architecture(vibe)
        if not plan or "components" not in plan:
            print("Planning failed. Episode is aborted")
            return 0.0
        self.pm.setup_project() ##Initialise fresh sandbox

        generated_code_map = {}
        for comp in plan['components']:
            print(f"Building component: {comp['name']}....")
            context = self.vs.search(f"{vibe} {comp['name']}") ##This is the RAG Search: Find relevant verified memories for the specific component

            raw_code = self.builder.generate_component(
                comp['name'],
                comp['description'],
                context_snippets=context
            )
            clean_code = self.healer.clean_code(raw_code)
            self.pm.write_component(comp['name'], clean_code)
            generated_code_map[comp['name']] = clean_code
        
        attempt = 1
        reward= 0.0
        final_status= "FAILED"

        while attempt <=max_retries:
            sandbox_code = self.assemble_sandbox_app(generated_code_map)
            inject_code(sandbox_code)
            success, logs = self.pm.run_validation()
            reward = self.calculate_composite_reward(success,logs, plan)

            print(f"[Attempt {attempt}] Running Global validation:Reward : {reward}")
            print(f"Debug TSC Logs: {logs}")

            if success and reward > 0.8:
                print(f"Success! Reward: {reward}")
                final_status = "VERIFIED"
                break
            else:
                print(f"Failure (Reward:{reward})")
                for name in generated_code_map:
                    if name.lower() in logs.lower() or f"{name}.tsx" in logs.lower():
                        print(f"Healing {name}....")
                        fixed_code = self.healer.heal(name,generated_code_map[name],logs)
                        self.pm.write_component(name, fixed_code)
                        generated_code_map[name] = fixed_code
                attempt += 1
       # print("Max retries reached. Episode Failed!")
        duration = time.time() - start_time
        self.save_experience(vibe, plan, generated_code_map, reward, final_status, duration)
        return reward
    def save_experience(self, vibe, plan, code_map, reward, status, duration):
        experience = {
            "vibe": vibe,
            "blueprint":plan,
            "code": code_map,
            "reward": reward,
            "status": status,
            "duration": round(duration,2),
            "timestamp": time.time()
        }
        if status == "VERIFIED":
            self.vs.add(experience)
            print(f"Experience saved in Vector Store: {status}(Reward: {reward})")
        log_file = "data/synthetic_dataset_100.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(experience) + "\n") 

        print(f"Logged to {log_file}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    orchestrator = RLOrchestrator()
    #prober = Prober()
    task_gen = TaskProber()
    TOTAL_EPISODES = 100
    DATASET_PROMPTS = task_gen.generate_batch(TOTAL_EPISODES)
    print(f"Starting Synthetic Data loop for {TOTAL_EPISODES} episodes")
    print(f"Model running....")
    for i, prompt in enumerate(DATASET_PROMPTS):
        print(f"\n Progress: {i+1}/{TOTAL_EPISODES} ---")
        try:
            orchestrator.run_episode(prompt, episode_id=i+1)
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n Training paused: By User")
            break
        except Exception as e:
            print(f"Critical error in Episode {i+1}:{e}")
            continue
    print(f"Synthetic data-gen complete!")       
