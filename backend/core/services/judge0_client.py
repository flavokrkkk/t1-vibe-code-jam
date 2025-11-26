import logging
import aiohttp
import base64
from core.config.config import settings
from infrastructure.errors.base import BadRequestException

logger = logging.getLogger(__name__)

LANGUAGE_IDS = {
    "python": 71,  # Python 3.8.1 (3.10 available in newer images)
    "go": 60,      # Go 1.13.5
    "javascript": 63, # Node.js 12.14.0
    "js": 63
}

class Judge0Client:
    def __init__(self):
        self.base_url = settings.JUDGE0_API_URL  # e.g. http://judge0-server:2358
        if not self.base_url:
            self.base_url = "http://judge0-server:2358"

    async def run_code(self, source_code: str, language: str, stdin: str = "", expected_output: str = ""):
        language_id = LANGUAGE_IDS.get(language.lower())
        if not language_id:
            raise BadRequestException(f"Unsupported language: {language}")

        url = f"{self.base_url}/submissions?base64_encoded=true&wait=true"
        
        # Encode inputs to base64 to avoid issue with special chars
        payload = {
            "source_code": base64.b64encode(source_code.encode()).decode(),
            "language_id": language_id,
            "stdin": base64.b64encode(stdin.encode()).decode(),
            "expected_output": base64.b64encode(expected_output.encode()).decode() if expected_output else None
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 201 and response.status != 200:
                        text = await response.text()
                        logger.error(f"Judge0 Error: {text}")
                        raise BadRequestException("Failed to execute code on Judge0")
                    
                    result = await response.json()
                    
                    # Decode outputs
                    stdout = result.get("stdout")
                    stderr = result.get("stderr")
                    compile_output = result.get("compile_output")
                    
                    return {
                        "stdout": base64.b64decode(stdout).decode() if stdout else "",
                        "stderr": base64.b64decode(stderr).decode() if stderr else "",
                        "compile_output": base64.b64decode(compile_output).decode() if compile_output else "",
                        "status": result.get("status", {}),
                        "time": result.get("time"),
                        "memory": result.get("memory")
                    }
        except Exception as e:
            logger.error(f"Error connecting to Judge0: {e}")
            raise BadRequestException(f"Code execution service unavailable: {str(e)}")

    async def run_tests(self, source_code: str, language: str, test_cases: list[dict]):
        """
        Run code against multiple test cases.
        test_cases format: [{"input": "...", "output": "..."}]
        """
        results = []
        all_passed = True
        
        # For simplicity and KISS, running sequentially. 
        # Ideally, use batch submission endpoint of Judge0 /submissions/batch
        
        # Let's use batch submission if possible, but start with sequential for reliability if batch isn't configured
        # Actually, batch is better.
        
        submissions = []
        language_id = LANGUAGE_IDS.get(language.lower())
        if not language_id:
            raise BadRequestException(f"Unsupported language: {language}")

        url = f"{self.base_url}/submissions/batch?base64_encoded=true&wait=true"

        for test in test_cases:
            submissions.append({
                "source_code": base64.b64encode(source_code.encode()).decode(),
                "language_id": language_id,
                "stdin": base64.b64encode(test.get("input", "").encode()).decode(),
                "expected_output": base64.b64encode(test.get("output", "").encode()).decode()
            })

        payload = {"submissions": submissions}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 201 and response.status != 200:
                         # Fallback to sequential if batch fails or returns error
                        logger.error(f"Judge0 Batch Error: {await response.text()}")
                        raise BadRequestException("Failed to execute batch tests")
                    
                    batch_results = await response.json()
                    
                    for res in batch_results:
                        stdout = res.get("stdout")
                        stderr = res.get("stderr")
                        status = res.get("status", {})
                        
                        decoded_stdout = base64.b64decode(stdout).decode() if stdout else ""
                        
                        passed = status.get("id") == 3 # Accepted
                        if not passed:
                            all_passed = False
                            
                        results.append({
                            "passed": passed,
                            "status": status.get("description"),
                            "stdout": decoded_stdout,
                            "stderr": base64.b64decode(stderr).decode() if stderr else "",
                            "expected": base64.b64decode(res.get("expected_output", "")).decode() if res.get("expected_output") else ""
                        })
                        
        except Exception as e:
             logger.error(f"Error in batch execution: {e}")
             raise BadRequestException("Error running tests")

        return {
            "all_passed": all_passed,
            "results": results
        }


