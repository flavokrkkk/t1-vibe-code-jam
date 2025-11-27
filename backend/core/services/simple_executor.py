"""
Простой executor для кода без Judge0
ТОЛЬКО ДЛЯ РАЗРАБОТКИ! В продакшене использовать Judge0 на Linux.
"""
import asyncio
import logging
import tempfile
import os
import json
from typing import Any

logger = logging.getLogger(__name__)


class SimpleExecutor:
    """Простой executor для Python кода. НЕ БЕЗОПАСЕН! Только для разработки."""
    
    async def run_tests(self, source_code: str, language: str, test_cases: list[dict]) -> dict[str, Any]:
        """
        Запускает тесты для кода.
        ВНИМАНИЕ: Выполняет код без изоляции! Только для разработки!
        """
        language_lower = language.lower()
        
        if language_lower not in ["python", "javascript", "js"]:
            return {
                "all_passed": False,
                "results": [{"passed": False, "status": "Unsupported language", "stdout": "", "stderr": f"Only Python and JavaScript supported in dev mode, got {language}", "expected": ""} for _ in test_cases]
            }
        
        results = []
        all_passed = True
        
        for test_case in test_cases:
            test_input = test_case.get("input", "")
            expected_output = test_case.get("output", "")
            
            try:
                # Создаем исполняемый код
                executable_code = self._create_executable_code(source_code, test_input, language_lower)
                
                # Определяем расширение и команду запуска
                if language_lower in ["javascript", "js"]:
                    suffix = '.js'
                    run_command = 'node'
                else:
                    suffix = '.py'
                    run_command = 'python'
                
                # Создаем временный файл
                with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
                    f.write(executable_code)
                    temp_file = f.name
                
                try:
                    # Запускаем с timeout
                    process = await asyncio.create_subprocess_exec(
                        run_command, temp_file,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    try:
                        stdout, stderr = await asyncio.wait_for(
                            process.communicate(),
                            timeout=5.0  # 5 секунд timeout
                        )
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()
                        results.append({
                            "passed": False,
                            "status": "Time Limit Exceeded",
                            "stdout": "",
                            "stderr": "Execution timeout (5s)",
                            "expected": expected_output
                        })
                        all_passed = False
                        continue
                    
                    stdout_str = stdout.decode('utf-8').strip()
                    stderr_str = stderr.decode('utf-8').strip()
                    
                    # Нормализуем вывод для сравнения
                    normalized_stdout = self._normalize_output(stdout_str)
                    normalized_expected = self._normalize_output(expected_output)
                    
                    passed = normalized_stdout == normalized_expected and process.returncode == 0
                    
                    if not passed:
                        all_passed = False
                    
                    status = "Accepted" if passed else ("Runtime Error" if stderr_str else "Wrong Answer")
                    
                    results.append({
                        "passed": passed,
                        "status": status,
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                        "expected": expected_output
                    })
                    
                finally:
                    # Удаляем временный файл
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"Error executing code: {e}", exc_info=True)
                results.append({
                    "passed": False,
                    "status": "Internal Error",
                    "stdout": "",
                    "stderr": str(e),
                    "expected": expected_output
                })
                all_passed = False
        
        return {
            "all_passed": all_passed,
            "results": results
        }
    
    def _normalize_output(self, output: str) -> str:
        """Нормализует вывод для сравнения."""
        # Убираем пробелы в начале/конце
        output = output.strip()
        
        # Пробуем распарсить как JSON для нормализации
        try:
            parsed = json.loads(output)
            return json.dumps(parsed, separators=(',', ':'), sort_keys=True)
        except:
            pass
        
        # Если не JSON, возвращаем как есть
        return output
    
    def _create_executable_code(self, source_code: str, test_input: str, language: str = "python") -> str:
        """Создает исполняемый код с wrapper'ом."""
        
        if language in ["javascript", "js"]:
            return self._create_javascript_executable(source_code, test_input)
        
        # Python код
        # Сначала перехватываем stdout, ПОТОМ идет код пользователя
        header = """
# Перехватываем stdout ДО выполнения кода пользователя
import sys
import io
_original_stdout = sys.stdout
sys.stdout = io.StringIO()  # Игнорируем все print() от пользователя
"""
        
        wrapper_code = """
# Test execution wrapper
import json

if __name__ == "__main__":
    try:
        # Входные данные из теста
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
        
        # Если input пустой - вызываем без параметров
        if not test_input or not test_input.strip():
            result = method()
        else:
            # Пробуем распарсить как JSON
            try:
                input_data = json.loads(test_input)
                
                # Если input_data - это dict с именованными параметрами
                if isinstance(input_data, dict):
                    try:
                        result = method(**input_data)
                    except TypeError:
                        result = method(input_data)
                        
                # Если input_data - это list с позиционными аргументами
                elif isinstance(input_data, list):
                    result = method(*input_data)
                    
                # Иначе передаем как единственный аргумент
                else:
                    result = method(input_data)
                    
            except (json.JSONDecodeError, TypeError) as e:
                # Если не JSON или ошибка типа - передаем как строку
                result = method(test_input.strip())
        
        # Восстанавливаем stdout для вывода результата
        sys.stdout = _original_stdout
        
        # Выводим результат (в Python формате, не JSON)
        if result is None:
            print("None")
        elif isinstance(result, bool):
            # Python boolean: True/False (не JSON true/false)
            print("True" if result else "False")
        elif isinstance(result, (list, dict)):
            # Для list/dict используем JSON формат
            print(json.dumps(result, separators=(',', ':')))
        elif isinstance(result, str):
            # Строки без кавычек (как в Python print)
            print(result)
        else:
            print(result)
            
    except Exception as e:
        import traceback
        # Восстанавливаем stdout перед выводом ошибки
        try:
            sys.stdout = _original_stdout
        except:
            pass
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
"""
        # Заменяем placeholder на реальные данные
        test_input_repr = json.dumps(test_input)
        wrapper_code = wrapper_code.replace("TEST_INPUT_DATA", test_input_repr)
        
        # Важно: header (перехват stdout) -> source_code (код пользователя) -> wrapper (выполнение)
        return header + "\n" + source_code + "\n" + wrapper_code
    
    def _create_javascript_executable(self, source_code: str, test_input: str) -> str:
        """Создает исполняемый JavaScript код с wrapper'ом."""
        import json as json_lib
        
        # Экранируем test_input для вставки в JS код
        test_input_json = json_lib.dumps(test_input)
        
        header = """
// Перехватываем console.log ДО выполнения кода пользователя
const originalLog = console.log;
console.log = () => {}; // Игнорируем все console.log() от пользователя
"""
        
        wrapper = f"""
// Test execution wrapper
(async () => {{
    try {{
        const testInput = {test_input_json};
        
        // Восстанавливаем console.log для вывода результата
        console.log = originalLog;
        
        // Создаем экземпляр Solution
        const sol = new Solution();
        
        // Находим первый метод (кроме constructor)
        const methodNames = Object.getOwnPropertyNames(Solution.prototype)
            .filter(name => name !== 'constructor');
        
        if (methodNames.length === 0) {{
            console.error('Error: No public method found in Solution class');
            process.exit(1);
        }}
        
        const methodName = methodNames[0];
        const method = sol[methodName].bind(sol);
        
        let result;
        
        // Если input пустой - вызываем без параметров
        if (!testInput || !testInput.trim()) {{
            result = method();
        }} else {{
            // Пробуем распарсить как JSON
            try {{
                const inputData = JSON.parse(testInput);
                
                // Если inputData - это object с именованными параметрами
                if (typeof inputData === 'object' && !Array.isArray(inputData) && inputData !== null) {{
                    // Передаем значения как аргументы
                    result = method(...Object.values(inputData));
                }} else if (Array.isArray(inputData)) {{
                    // Если это массив - передаем как spread
                    result = method(...inputData);
                }} else {{
                    // Иначе передаем как единственный аргумент
                    result = method(inputData);
                }}
            }} catch (e) {{
                // Если не JSON - передаем как строку
                result = method(testInput.trim());
            }}
        }}
        
        // Выводим результат
        if (result === null) {{
            console.log('null');
        }} else if (typeof result === 'boolean') {{
            console.log(result ? 'true' : 'false');
        }} else if (typeof result === 'object') {{
            console.log(JSON.stringify(result));
        }} else if (typeof result === 'string') {{
            console.log(result);
        }} else {{
            console.log(result);
        }}
        
    }} catch (e) {{
        console.log = originalLog;
        console.error('Error:', e.message);
        console.error(e.stack);
        process.exit(1);
    }}
}})();
"""
        
        return header + "\n" + source_code + "\n" + wrapper

