##main loop contains all builder, healer and evaluator
from builder import Builder
from evaluator import Evaluator
from healer import Healer
import time
from prober import Prober
def run_self_healing(prompt, max_retries=3):
    builder = Builder()
    evaluator = Evaluator()
    healer = Healer(builder)
    prober = Prober()
    print(f"\n ['Vibe' Request]: {prompt}")

    raw_code = builder.generate_component(prompt)
    current_code = healer.clean_code(raw_code) ##In case LLM ignores instructions and wraps in markdown, we clean it here before eval
    attempt = 1

    while attempt <= max_retries:
        print(f"[Attempt {attempt}] : Evaluating code...")
        score, error_msg = evaluator.check_syntax(current_code)

        if score == 1.0:
            print("[Success!!] Code is functional and usable!")
            return current_code
        else:
            print(f"[Failure]: Reward Score is 0.0. Healing Required!!")
            current_code = healer.heal(current_code, error_msg)
            attempt += 1
            #time.sleep(2) # Small Puase for Local LLM Processing
    print("[ERROR!!] Max retries reached. Vibe ain't healin' itself.")
    return None

if __name__ == "__main__":
    prober = Prober()
    for vibe in prober.get_challenges():
        run_self_healing(vibe)