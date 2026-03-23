#Updated prober.py
#Performs the action of injection and validation by using Teacher-Student RL System
#Remving the Task Selector logic and making it capable of making changes to GeneratedApp.js
#Uses watchdog to ensure react dev server is actually seeing the changes.

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

TARGET_FILE =os.path.join("rn_web_template", "src", "GeneratedApp.js")

class SandboxHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("GeneratedApp.js"):
            print(f"[Sandbox] Hot-reload triggered at {time.strftime('%H:%M:%S')}")

def inject_code(code_string):
    try: 
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write(code_string)
        print("[Prober] injected new code to sandbox!")
    except Exception as e:
        print(f"[eRROr] Failed to inject code:{e}")

if __name__ == "__main__":
    event_handler = SandboxHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(TARGET_FILE), recursive=False)
    observer.start()

    print(f"Watching {TARGET_FILE} for changes...")

    try:
        test_ui = """
import React from 'react';
import { View, Text } from 'react-native';

export default function GeneratedApp() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#282c34' }}>
      <Text style={{ color: '#61dafb', fontSize: 30 }}>RL Agent Update #1</Text>
    </View>
  );
}
"""
        time.sleep(2)
        inject_code(test_ui)

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()            