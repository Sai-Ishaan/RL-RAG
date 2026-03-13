### The following is a demo to explore bridging the Gap between Static RAG and Functional Code Generation. 

### Key tools used:
 -- LangGraph: Fpr building multi-step "agentic" logic.

 -- Convex: BaaS, to build a prototype backend.

 -- DeepSpeed-Chat: (RLHF/RLAIF) for Model Alignment.


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