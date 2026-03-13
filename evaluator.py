import subprocess
import os

class Evaluator:
    def __init__(self, temp_file="sandbox_test.tsx"):
        self.temp_file = temp_file

    def check_syntax(self, code: str):
        ###Runs tsc against code string and returns Score and Err Msg

        with open(self.temp_file, "w") as f:
            f.write(code)

        result = subprocess.run(
            ["npx", "tsc", self.temp_file, 
            "--noEmit",
            "--skipLibCheck", 
                "--jsx", "react-native",
                "--moduleResolution", "node",
                "--esModuleInterop", "true",
                "--lib", "esnext,dom"],
            capture_output=True,
            text=True,
            shell=True ##For Windows support
        )

        if result.returncode == 0:
            return 1.0, None ##Perfect Reward
        else:
            return 0.0, result.stdout ##0 reward and compiler's complaint

if __name__ == "__main__":
    evaluator = Evaluator()
##Test 1 good code
    good_code = """import React from 'react'; 
    import { Text } from 'react-native'; 
    const App = () => {
        return <Text> Hello There! </Text>
    };
    export default App;"""
    score, err = evaluator.check_syntax(good_code)
    print(f"Good Code Score: {score}")

    bad_code = "const App = () => <Text>Missing Import</Text>;"
    score, err = evaluator.check_syntax(bad_code)
    print(f"Bad Code Score: {score} | Error: {err[:50]}...")


