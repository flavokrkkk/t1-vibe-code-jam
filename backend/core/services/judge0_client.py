import logging
import aiohttp
import asyncio
import base64
import os
from core.config.config import settings
from infrastructure.errors.base import BadRequestException

logger = logging.getLogger(__name__)

# Флаг для использования простого executor вместо Judge0 (для Windows/разработки)
USE_SIMPLE_EXECUTOR = os.getenv("USE_SIMPLE_EXECUTOR", "false").lower() == "true"

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
    
    def _create_executable_code(self, source_code: str, test_input: str, language: str) -> str:
        """
        Создает полный исполняемый код для Judge0 с вызовом метода Solution.
        source_code: код класса/функции пользователя
        test_input: входные данные для теста (в JSON формате или простой строкой)
        language: язык программирования
        """
        import json as json_lib
        language = language.lower()
        
        if language == "python":
            # Для Python формируем код с вызовом метода Solution
            # Обрабатываем различные форматы test_input
            parsed_input = test_input
            
            if isinstance(test_input, str):
                # Пробуем распарсить как JSON
                try:
                    parsed_input = json_lib.loads(test_input)
                except json_lib.JSONDecodeError:
                    # Если не валидный JSON, пробуем исправить "[1,2,3], 9" -> [[1,2,3], 9]
                    if ',' in test_input and not test_input.startswith('['):
                        # Простой случай: "arg1, arg2" -> [arg1, arg2]
                        try:
                            parsed_input = json_lib.loads(f"[{test_input}]")
                        except:
                            # Если не получилось - оставляем как строку
                            parsed_input = test_input
                    else:
                        # Оставляем как строку
                        parsed_input = test_input
            
            # Сериализуем для безопасной вставки в код
            test_input_repr = json_lib.dumps(parsed_input)
            
            wrapper_code = """
# Test execution wrapper
import sys
import json

if __name__ == "__main__":
    try:
        # Входные данные из теста (уже распарсены из JSON)
        test_input = json.loads(TEST_INPUT_DATA)
        
        # Создаем экземпляр Solution
        sol = Solution()
        
        # Находим первый не-дандер метод
        method_name = None
        for attr_name in dir(sol):
            if not attr_name.startswith('_') and callable(getattr(sol, attr_name)):
                method_name = attr_name
                break
        
        if not method_name:
            print("Error: No public method found in Solution class", file=sys.stderr)
            sys.exit(1)
        
        method = getattr(sol, method_name)
        result = None
        
        # Проверяем тип входных данных
        if test_input is None or test_input == "" or test_input == []:
            # Пустой input - вызываем без параметров
            result = method()
        elif isinstance(test_input, dict):
            # Dict с именованными параметрами: {"nums": [1,2,3], "target": 9}
            try:
                result = method(**test_input)
            except TypeError:
                # Если не подошло, пробуем передать весь dict как один аргумент
                result = method(test_input)
        elif isinstance(test_input, list):
            # List с позиционными аргументами: [[1,2,3], 9]
            result = method(*test_input)
        else:
            # Примитивный тип (str, int, etc.) - передаем как единственный аргумент
            result = method(test_input)
        
        # Выводим результат
        if result is None:
            print("null")
        elif isinstance(result, bool):
            print("true" if result else "false")
        elif isinstance(result, (list, dict)):
            print(json.dumps(result, separators=(',', ':')))
        elif isinstance(result, str):
            print(json.dumps(result))
        else:
            print(result)
            
    except Exception as e:
        import traceback
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
"""
            # Заменяем placeholder на реальные данные
            wrapper_code = wrapper_code.replace("TEST_INPUT_DATA", test_input_repr)
            
            return source_code + "\n" + wrapper_code
        
        elif language in ["javascript", "js"]:
            # Для JavaScript
            return f'''{source_code}

// Test execution wrapper
const testInput = `{test_input}`;

try {{
    let result;
    const sol = new Solution();
    
    if (testInput.trim()) {{
        const inputData = JSON.parse(testInput);
        const methodName = Object.getOwnPropertyNames(Solution.prototype)
            .filter(name => name !== 'constructor')[0];
        
        if (Array.isArray(inputData)) {{
            result = sol[methodName](...inputData);
        }} else if (typeof inputData === 'object') {{
            result = sol[methodName](...Object.values(inputData));
        }} else {{
            result = sol[methodName](inputData);
        }}
    }}
    
    console.log(typeof result === 'object' ? JSON.stringify(result) : result);
}} catch (e) {{
    console.error('Error:', e.message);
    process.exit(1);
}}
'''
        
        elif language == "go":
            # Для Go просто возвращаем код как есть (пользователь должен написать main)
            return source_code
        
        else:
            # Для других языков возвращаем код как есть
            return source_code

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
        # Если используем простой executor (для Windows/разработки)
        if USE_SIMPLE_EXECUTOR:
            logger.info("Using SimpleExecutor instead of Judge0 (development mode)")
            from core.services.simple_executor import SimpleExecutor
            executor = SimpleExecutor()
            return await executor.run_tests(source_code, language, test_cases)
        
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

        # Step 1: Submit batch (POST returns only tokens)
        submit_url = f"{self.base_url}/submissions/batch?base64_encoded=true"
        
        # Формируем исполняемый код для каждого теста
        for idx, test in enumerate(test_cases):
            executable_code = self._create_executable_code(
                source_code, 
                test.get("input", ""), 
                language
            )
            
            logger.debug(f"Test {idx+1} executable code:\n{executable_code[:500]}...")
            logger.debug(f"Test {idx+1} input: {test.get('input', '')}")
            logger.debug(f"Test {idx+1} expected output: {test.get('output', '')}")
            
            submissions.append({
                "source_code": base64.b64encode(executable_code.encode()).decode(),
                "language_id": language_id,
                "stdin": "",  # Входные данные уже в коде
                "expected_output": base64.b64encode(test.get("output", "").encode()).decode()
            })

        payload = {"submissions": submissions}

        try:
            logger.info(f"Sending to Judge0: {len(submissions)} submissions")
            logger.debug(f"Test cases: {test_cases}")
            
            async with aiohttp.ClientSession() as session:
                # Step 1: Submit batch and get tokens
                async with session.post(submit_url, json=payload) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        logger.error(f"Judge0 Batch submission failed: status={response.status}, response={error_text}")
                        raise BadRequestException("Failed to submit batch tests")
                    
                    token_results = await response.json()
                    logger.info(f"Judge0 tokens received: {len(token_results)}")
                    logger.debug(f"Tokens: {token_results}")
                
                # Step 2: Fetch results by tokens
                tokens = [r["token"] for r in token_results]
                tokens_param = ",".join(tokens)
                fetch_url = f"{self.base_url}/submissions/batch?tokens={tokens_param}&base64_encoded=true"
                
                # Poll for results (max 15 attempts with 0.5s delay)
                batch_results = None
                for attempt in range(15):
                    await asyncio.sleep(0.5)
                    async with session.get(fetch_url) as response:
                        if response.status != 200:
                            logger.warning(f"Attempt {attempt+1}: Failed to fetch results: {response.status}")
                            continue
                        
                        fetched_data = await response.json()
                        
                        # Judge0 batch GET returns {"submissions": [...]}
                        submissions_data = fetched_data.get("submissions", fetched_data)
                        
                        # Check if all submissions are done (status_id not in [1=In Queue, 2=Processing])
                        if isinstance(submissions_data, list):
                            all_done = all(
                                s.get("status", {}).get("id") not in [1, 2] 
                                for s in submissions_data
                            )
                            if all_done:
                                batch_results = submissions_data
                                logger.info(f"All submissions completed after {attempt+1} attempts")
                                break
                        else:
                            logger.warning(f"Unexpected response format: {fetched_data}")
                
                if not batch_results:
                    raise BadRequestException("Failed to fetch code execution results after polling")
                
                logger.info(f"Judge0 final results: {len(batch_results)} submissions")
                logger.info(f"Full Judge0 results: {batch_results}")
                
                for idx, res in enumerate(batch_results):
                    logger.info(f"Processing result {idx}: {res}")
                    
                    stdout = res.get("stdout")
                    stderr = res.get("stderr")
                    status = res.get("status") or {}
                    
                    decoded_stdout = base64.b64decode(stdout).decode() if stdout else ""
                    decoded_stderr = base64.b64decode(stderr).decode() if stderr else ""
                    decoded_expected = base64.b64decode(res.get("expected_output", "")).decode() if res.get("expected_output") else ""
                    
                    logger.debug(f"Test result: status_id={status.get('id')}, stdout='{decoded_stdout}', stderr='{decoded_stderr}', expected='{decoded_expected}'")
                    
                    passed = status.get("id") == 3 # Accepted
                    if not passed:
                        all_passed = False
                        logger.warning(f"Test failed: status={status.get('description')}, stdout='{decoded_stdout}', stderr='{decoded_stderr}'")
                        
                    results.append({
                        "passed": passed,
                        "status": status.get("description"),
                        "stdout": decoded_stdout,
                        "stderr": decoded_stderr,
                        "expected": decoded_expected
                    })
                        
        except Exception as e:
             logger.error(f"Error in batch execution: {e}")
             raise BadRequestException("Error running tests")

        return {
            "all_passed": all_passed,
            "results": results
        }


