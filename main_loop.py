##main loop contains all builder, healer and evaluator
from builder import Builder
from evaluator import Evaluator
from healer import Healer
import time
from architect import Architect
from prober import Prober
import json
from project_manager import ProjectManager
from vector_store import VectorStore

class RLOrchestrator:
    def __init__(self):
        self.builder = Builder()
        self.evaluator = Evaluator()
        self.healer = Healer(self.builder)
        self.architect = Architect(self.builder.client)
        self.pm = ProjectManager()
        self.prober = Prober()
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
    
    def run_episode(self, vibe, max_retries=2):
        ###Executes every single RL episode for a given prompt or vibe
        print(f"\n --- [New Episode] {vibe} --- ")
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
        while attempt <=max_retries:
            print(f"[Attempt {attempt}] Running Global validation:")
            success, logs = self.pm.run_validation()
            print(f"Debug TSC Logs: {logs}")
            reward = self.calculate_composite_reward(success, logs, plan)

            if success and reward > 0.7:
                print(f"Success! Reward: {reward}")
                self.save_experience(vibe, plan, generated_code_map,reward, "VERIFIED")
                return reward
            else:
                print(f"Failure (Reward:{reward})")
                for name in generated_code_map:
                    if name.lower() in logs.lower() or f"{name}.tsx" in logs.lower():
                        print(f"Healing {name}....")
                        fixed_code = self.healer.heal(name,generated_code_map[name],logs)
                        self.pm.write_component(name, fixed_code)
                        generated_code_map[name] = fixed_code
                attempt += 1
        print("Max retries reached. Episode Failed!")
        self.save_experience(vibe, plan, generated_code_map, reward, "FAILED")
        return reward
    # def run_rl_orchestrator(self, vibe, max_retries=3):
    #     print(f"\n New vibe: {vibe} \n")
    #     plan = self.architect.plan_architecture(vibe)
    #     if not plan or "error" in plan or "components" not in plan:
    #         print("Plan Generation Failed!!")
    #         return 0.0

    #     #self.pm.setup_project() ##Not implemented, but would create tsconfig, package.json etc.
    #     generated_files = {}
    #     for comp in plan['components']:
    #         print(f"Building: {comp['name']}....")
    #         ##context = ""

    #         raw_code = self.builder.generate_component(comp['description'], context_snippets="")
    #         clean_code = self.healer.clean_code(raw_code)

    #         self.pm.write_component(comp['name'], clean_code)
    #         generated_files[comp['name']] = clean_code
    #     attempt = 1 #Global Evaluation + Healing
    #     reward = 0.0

    #     while attempt <= max_retries:
    #         print(f"Attempt{attempt}: Global Validation...")
    #         success, logs = self.pm.run_validation()

    #         reward = self.calculate_composite_reward(success, logs, plan)

    #         if success and reward > 0.7:
    #             print(f"Success! Reward: {reward}")
    #             self.save_experience(vibe, plan, reward, "VERIFIED")
    #             return reward
    #         print(f" Reward: {reward}. Scanning logs for healing targets...")

    #         files_healed_this_turn = 0 #A check variable that acknowledges any global error than just staying silent
    #         for comp_name in generated_files:
    #             if comp_name.lower() in logs.lower():
    #                 print(f"Healing {comp_name}...")
    #                 fixed_code = self.healer.heal(generated_files[comp_name], logs)
    #                 self.pm.write_component(comp_name, fixed_code)
    #                 generated_files[comp_name] = fixed_code
    #                 files_healed_this_turn += 1
            
    #         if files_healed_this_turn == 0:
    #             print("❗ No specific components identified in logs. Attempting general fix...")
            
    #         attempt += 1
    #     print("Max retries reached! Experience marked as FAILED!")
    #     self.save_experience(vibe, plan, reward, "FAILED")
    #     return reward

    def save_experience(self, vibe, plan, code_map, reward, status):
        experience = {
            "vibe": vibe,
            "blueprint":plan,
            "code": code_map,
            "reward": reward,
            "status": status
        }
        self.vs.add(experience)
        print(f"Experience saved in Vector Store: {status}(Reward: {reward})")

if __name__ == "__main__":
    orchestrator = RLOrchestrator()
    prober = Prober()

    for challenge_vibe in prober.get_challenges(2):
        orchestrator.run_episode(challenge_vibe)