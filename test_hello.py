#Test_hello

from main_loop import RLOrchestrator

def run_manual_hello():
    orchestrator = RLOrchestrator()
    ##Using a simple vibe that shouldn't require complex scripting
    vibe = "A screen that displays 'Hello World' in large Bold text"

    print(f"Starting Manual Hello World test")
    reward = orchestrator.run_episode(vibe)

    if reward>= 0.7:
        print(f"Success!! Hello World Score: {reward}")
    else:
        print(f"Test failed. Reward{reward}. Check project_sandbox")

if __name__ == "__main__":
    run_manual_hello()        