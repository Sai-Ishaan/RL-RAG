### The following is a demo to explore bridging the Gap between Static RAG and Functional Code Generation. 

### Technical Stack:
   --Orchestrator: Python 3.10
   --The Brain: Ollama(Local LLM Interface)
   --Judge: NodeJs + 'tsc' (TypeScript Compiler)
   --Target Stack: React Native

### Instructions:
  -- Make sure you've setup your virtual env using python -m venv venv.
  -- Open a Separate terminal and run : *ollama run llama3*
  -- Install the following dependencies and libraries: 
      pydantic, subprocess, typescript, @types/react, @types/react-native, @types/node 
  -- Define a Vibe Bank in your Prober in order to test the RL:
  def __init__(self):
        self.vibe_bank = [
            "A dark mode login screen with email/password fields and transparent background",
            "A profile card with an avatar, name and Follow Button",
            "A search bar that shows a 'No results' text when typed in",
            "A counter component with big '+' and '-' buttons",
            "A toggle switches that changes background color"
        ]
    Output:
    ### System in Action (Terminal Logs)

**Challenge:** "A profile card with an avatar, name and Follow Button"

```text
[Attempt 1] : Evaluating code...
[Failure]: Reward Score 0.0. 
[Error]: TS2304: Cannot find name 'TouchableOpacity'.

[Attempt 2] : Healing... (Injected Fix)
[Success!!] Code is functional and usable!
![alt text](image.png)

### _Why RL-RAG?_
  -- Feedback Loop(RL): Human-in-the-loop feedback is quite common. Building an RL Reward system based on compilation success and UI Testing allows agents to "practice" building(in this example, building native apps) without human supervision.

  -- Synthetic Data Strategy: 
  A strategy incorporated in order to keep indexes fresh. This solves the major problem of "Cold Starting", i.e:- updates and library version releases might take time to be incorporated into real-world examples. This sytem could generate thousands of "synthetic" apps using the new library to train the Agent before user asks.

This will work as a *_Self Healing Code Retrieval Layer_*.

### How does this Self-Healing Loop Work??

 -- Dividing into a three-stage factory:

   i) The Architect(Agentic RAG): The user asks for a feature. Agent pulls code from vectory store and Convex docs

   ii) Quality Control: Before displaying the code to user, the script sends it to a sandbox(like a Web Worker). It runs npm run build or linter

   iii) Learning(RL Reward system):
   If Success, code is tagged as Verified. Else if Failure, error log is sent to Refiner LLM, It fixes the code and _fix_ is stored as a new synthetic example. The original snippet which failed will recieve a negative reward.

### Current Benchmarks:
Performance Benchmarks
Tested using **Qwen-2.5-Coder** (Local) and **TypeScript 5.x**:

- **First-Pass Success Rate:** 60% (3/5 Challenges)
- **Recovery Rate:** High success in resolving basic syntax/import hallucinations.
- **Identified Edge Cases:** Complex conditional rendering (Search Bar logic) requires higher-reasoning models or better RAG context.

### Roadmap & Next Steps
- **Vector Store Integration:** Moving from local JSON mocks to a live Pinecone/Weaviate index to store "Verified" snippets.
- **Linter Integration:** Adding ESLint to the 'Quality Control' stage for code-style enforcement.
- **Synthetic Dataset Expansion:** Automating the 'Prober' to generate 1,000+ app scenarios to pre-train the Agentic RAG layer.
