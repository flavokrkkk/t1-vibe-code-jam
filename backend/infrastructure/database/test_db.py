"""
Инициализация тестовых данных в БД
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.database.models.models import CodeTask

logger = logging.getLogger(__name__)


async def init_test_db(session: AsyncSession):
    """
    Инициализирует тестовые задачи в БД, если их еще нет
    """
    try:
        # Проверяем, есть ли уже задачи в БД
        result = await session.execute(select(CodeTask).limit(1))
        existing_task = result.scalar_one_or_none()
        
        if existing_task:
            logger.info("Тестовые задачи уже существуют в БД, пропускаем инициализацию")
            return
        
        logger.info("Инициализация тестовых задач в БД...")
        
        tasks = [
            CodeTask(
                description="""**Two Sum**

Дан массив целых чисел `nums` и целое число `target`. Верните индексы двух чисел, которые в сумме дают `target`.

Пример:
- Input: nums = [2,7,11,15], target = 9
- Output: [0,1]

Класс должен называться Solution, метод - twoSum""",
                difficulty="easy",
                language="python",
                topic="Arrays",
                tags=["array", "hash-table"],
                test_cases={
                    "test_cases": [
                        {"input": "[[2, 7, 11, 15], 9]", "expected_output": "[0,1]"},
                        {"input": "[[3, 2, 4], 6]", "expected_output": "[1,2]"},
                        {"input": "[[3, 3], 6]", "expected_output": "[0,1]"}
                    ]
                },
                initial_code="""class Solution(object):
    def twoSum(self, nums, target):
        pass
"""
            ),
            
            CodeTask(
                description="""**Palindrome Number**

Дано целое число `x`, верните `true`, если `x` является палиндромом, и `false` в противном случае.

Пример:
- Input: x = 121
- Output: true

Класс должен называться Solution, метод - isPalindrome""",
                difficulty="easy",
                language="python",
                topic="Math",
                tags=["math"],
                test_cases={
                    "test_cases": [
                        {"input": "[121]", "expected_output": "True"},
                        {"input": "[-121]", "expected_output": "False"},
                        {"input": "[10]", "expected_output": "False"}
                    ]
                },
                initial_code="""class Solution(object):
    def isPalindrome(self, x):
        pass
"""
            ),
            
            CodeTask(
                description="""**Reverse String**

Напишите функцию, которая переворачивает строку. Входная строка дается в виде массива символов `s`.

Пример:
- Input: s = ["h","e","l","l","o"]
- Output: ["o","l","l","e","h"]

Класс должен называться Solution, метод - reverseString""",
                difficulty="easy",
                language="python",
                topic="String",
                tags=["string", "two-pointers"],
                test_cases={
                    "test_cases": [
                        {"input": '[[["h","e","l","l","o"]]]', "expected_output": '["o","l","l","e","h"]'},
                        {"input": '[[["H","a","n","n","a","h"]]]', "expected_output": '["h","a","n","n","a","H"]'}
                    ]
                },
                initial_code="""class Solution(object):
    def reverseString(self, s):
        pass
"""
            ),
            
            CodeTask(
                description="""**FizzBuzz**

Дано целое число `n`, верните строковый массив `answer` где:
- answer[i] == "FizzBuzz" если i делится на 3 и 5
- answer[i] == "Fizz" если i делится на 3
- answer[i] == "Buzz" если i делится на 5
- answer[i] == i (в виде строки) в противном случае

Пример:
- Input: n = 5
- Output: ["1","2","Fizz","4","Buzz"]

Класс должен называться Solution, метод - fizzBuzz""",
                difficulty="easy",
                language="python",
                topic="Math",
                tags=["math", "string"],
                test_cases={
                    "test_cases": [
                        {"input": "[3]", "expected_output": '["1","2","Fizz"]'},
                        {"input": "[5]", "expected_output": '["1","2","Fizz","4","Buzz"]'},
                        {"input": "[15]", "expected_output": '["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]'}
                    ]
                },
                initial_code="""class Solution(object):
    def fizzBuzz(self, n):
        pass
"""
            ),
            
            CodeTask(
                description="""**Valid Parentheses**

Дана строка `s`, содержащая только символы '(', ')', '{', '}', '[' и ']', определите, является ли входная строка валидной.

Пример:
- Input: s = "()"
- Output: true

Класс должен называться Solution, метод - isValid""",
                difficulty="medium",
                language="python",
                topic="Stack",
                tags=["stack", "string"],
                test_cases={
                    "test_cases": [
                        {"input": '["()"]', "expected_output": "True"},
                        {"input": '["()[]{}"]', "expected_output": "True"},
                        {"input": '["(]"]', "expected_output": "False"}
                    ]
                },
                initial_code="""class Solution(object):
    def isValid(self, s):
        pass
"""
            ),
            
            CodeTask(
                description="""**Maximum Subarray**

Дан целочисленный массив `nums`, найдите подмассив с наибольшей суммой и верните его сумму.

Пример:
- Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
- Output: 6

Класс должен называться Solution, метод - maxSubArray""",
                difficulty="medium",
                language="python",
                topic="Dynamic Programming",
                tags=["array", "dynamic-programming"],
                test_cases={
                    "test_cases": [
                        {"input": "[[-2,1,-3,4,-1,2,1,-5,4]]", "expected_output": "6"},
                        {"input": "[[1]]", "expected_output": "1"},
                        {"input": "[[5,4,-1,7,8]]", "expected_output": "23"}
                    ]
                },
                initial_code="""class Solution(object):
    def maxSubArray(self, nums):
        pass
"""
            ),
            
            CodeTask(
                description="""**Merge Two Sorted Lists**

Даны два отсортированных списка `list1` и `list2`. Объедините их в один отсортированный список.

Пример:
- Input: list1 = [1,2,4], list2 = [1,3,4]
- Output: [1,1,2,3,4,4]

Класс должен называться Solution, метод - mergeTwoLists""",
                difficulty="easy",
                language="python",
                topic="Linked List",
                tags=["linked-list", "recursion"],
                test_cases={
                    "test_cases": [
                        {"input": "[[[1,2,4], [1,3,4]]]", "expected_output": "[1,1,2,3,4,4]"},
                        {"input": "[[[], []]]", "expected_output": "[]"},
                        {"input": "[[[], [0]]]", "expected_output": "[0]"}
                    ]
                },
                initial_code="""class Solution(object):
    def mergeTwoLists(self, list1, list2):
        pass
"""
            ),
            
            CodeTask(
                description="""**Best Time to Buy and Sell Stock**

Дан массив `prices`, где `prices[i]` - это цена акции в i-й день. Найдите максимальную прибыль.

Пример:
- Input: prices = [7,1,5,3,6,4]
- Output: 5

Класс должен называться Solution, метод - maxProfit""",
                difficulty="easy",
                language="python",
                topic="Arrays",
                tags=["array", "dynamic-programming"],
                test_cases={
                    "test_cases": [
                        {"input": "[[7,1,5,3,6,4]]", "expected_output": "5"},
                        {"input": "[[7,6,4,3,1]]", "expected_output": "0"}
                    ]
                },
                initial_code="""class Solution(object):
    def maxProfit(self, prices):
        pass
"""
            ),
            
            CodeTask(
                description="""**Contains Duplicate**

Дан массив `nums`, верните `true`, если какое-либо значение появляется как минимум дважды.

Пример:
- Input: nums = [1,2,3,1]
- Output: true

Класс должен называться Solution, метод - containsDuplicate""",
                difficulty="easy",
                language="python",
                topic="Arrays",
                tags=["array", "hash-table"],
                test_cases={
                    "test_cases": [
                        {"input": "[[1,2,3,1]]", "expected_output": "True"},
                        {"input": "[[1,2,3,4]]", "expected_output": "False"}
                    ]
                },
                initial_code="""class Solution(object):
    def containsDuplicate(self, nums):
        pass
"""
            ),
            
            CodeTask(
                description="""**Binary Search**

Дан отсортированный массив `nums` и целое число `target`. Найдите `target` в `nums` за O(log n).

Пример:
- Input: nums = [-1,0,3,5,9,12], target = 9
- Output: 4

Класс должен называться Solution, метод - search""",
                difficulty="easy",
                language="python",
                topic="Binary Search",
                tags=["array", "binary-search"],
                test_cases={
                    "test_cases": [
                        {"input": "[[-1,0,3,5,9,12], 9]", "expected_output": "4"},
                        {"input": "[[-1,0,3,5,9,12], 2]", "expected_output": "-1"}
                    ]
                },
                initial_code="""class Solution(object):
    def search(self, nums, target):
        pass
"""
            ),
            
            CodeTask(
                description="""**Climbing Stairs**

Вы поднимаетесь по лестнице. Требуется n шагов. Каждый раз вы можете подняться на 1 или 2 ступени. Сколькими способами можно подняться наверх?

Пример:
- Input: n = 3
- Output: 3

Класс должен называться Solution, метод - climbStairs""",
                difficulty="easy",
                language="python",
                topic="Dynamic Programming",
                tags=["dynamic-programming", "math"],
                test_cases={
                    "test_cases": [
                        {"input": "[2]", "expected_output": "2"},
                        {"input": "[3]", "expected_output": "3"},
                        {"input": "[5]", "expected_output": "8"}
                    ]
                },
                initial_code="""class Solution(object):
    def climbStairs(self, n):
        pass
"""
            ),
            
            CodeTask(
                description="""**Reverse Linked List**

Дана голова односвязного списка, переверните список.

Пример:
- Input: head = [1,2,3,4,5]
- Output: [5,4,3,2,1]

Класс должен называться Solution, метод - reverseList""",
                difficulty="easy",
                language="python",
                topic="Linked List",
                tags=["linked-list", "recursion"],
                test_cases={
                    "test_cases": [
                        {"input": "[[1,2,3,4,5]]", "expected_output": "[5,4,3,2,1]"},
                        {"input": "[[1,2]]", "expected_output": "[2,1]"},
                        {"input": "[[]]", "expected_output": "[]"}
                    ]
                },
                initial_code="""class Solution(object):
    def reverseList(self, head):
        pass
"""
            ),
            
            CodeTask(
                description="""**Valid Anagram**

Даны две строки `s` и `t`, верните `true`, если `t` является анаграммой `s`.

Пример:
- Input: s = "anagram", t = "nagaram"
- Output: true

Класс должен называться Solution, метод - isAnagram""",
                difficulty="easy",
                language="python",
                topic="String",
                tags=["hash-table", "string", "sorting"],
                test_cases={
                    "test_cases": [
                        {"input": '["anagram", "nagaram"]', "expected_output": "True"},
                        {"input": '["rat", "car"]', "expected_output": "False"}
                    ]
                },
                initial_code="""class Solution(object):
    def isAnagram(self, s, t):
        pass
"""
            ),
            
            CodeTask(
                description="""**Longest Common Prefix**

Найдите самую длинную общую префиксную строку среди массива строк.

Пример:
- Input: strs = ["flower","flow","flight"]
- Output: "fl"

Класс должен называться Solution, метод - longestCommonPrefix""",
                difficulty="easy",
                language="python",
                topic="String",
                tags=["string"],
                test_cases={
                    "test_cases": [
                        {"input": '[[["flower","flow","flight"]]]', "expected_output": '"fl"'},
                        {"input": '[[["dog","racecar","car"]]]', "expected_output": '""'}
                    ]
                },
                initial_code="""class Solution(object):
    def longestCommonPrefix(self, strs):
        pass
"""
            ),
            
            CodeTask(
                description="""**Single Number**

Дан массив `nums`, где каждый элемент появляется дважды, кроме одного. Найдите этот элемент.

Пример:
- Input: nums = [2,2,1]
- Output: 1

Класс должен называться Solution, метод - singleNumber""",
                difficulty="easy",
                language="python",
                topic="Bit Manipulation",
                tags=["array", "bit-manipulation"],
                test_cases={
                    "test_cases": [
                        {"input": "[[2,2,1]]", "expected_output": "1"},
                        {"input": "[[4,1,2,1,2]]", "expected_output": "4"},
                        {"input": "[[1]]", "expected_output": "1"}
                    ]
                },
                initial_code="""class Solution(object):
    def singleNumber(self, nums):
        pass
"""
            ),
            
            CodeTask(
                description="""**Move Zeroes**

Дан массив `nums`, переместите все 0 в конец, сохраняя порядок ненулевых элементов.

Пример:
- Input: nums = [0,1,0,3,12]
- Output: [1,3,12,0,0]

Класс должен называться Solution, метод - moveZeroes""",
                difficulty="easy",
                language="python",
                topic="Arrays",
                tags=["array", "two-pointers"],
                test_cases={
                    "test_cases": [
                        {"input": "[[0,1,0,3,12]]", "expected_output": "[1,3,12,0,0]"},
                        {"input": "[[0]]", "expected_output": "[0]"}
                    ]
                },
                initial_code="""class Solution(object):
    def moveZeroes(self, nums):
        pass
"""
            ),
            
            CodeTask(
                description="""**Happy Number**

Определите, является ли число `n` счастливым. Счастливое число - это число, которое в процессе замены суммой квадратов цифр становится равным 1.

Пример:
- Input: n = 19
- Output: true

Класс должен называться Solution, метод - isHappy""",
                difficulty="easy",
                language="python",
                topic="Math",
                tags=["hash-table", "math"],
                test_cases={
                    "test_cases": [
                        {"input": "[19]", "expected_output": "True"},
                        {"input": "[2]", "expected_output": "False"}
                    ]
                },
                initial_code="""class Solution(object):
    def isHappy(self, n):
        pass
"""
            ),
            
            CodeTask(
                description="""**Power of Two**

Дано целое число `n`, верните `true`, если оно является степенью двойки.

Пример:
- Input: n = 16
- Output: true

Класс должен называться Solution, метод - isPowerOfTwo""",
                difficulty="easy",
                language="python",
                topic="Bit Manipulation",
                tags=["bit-manipulation", "math"],
                test_cases={
                    "test_cases": [
                        {"input": "[1]", "expected_output": "True"},
                        {"input": "[16]", "expected_output": "True"},
                        {"input": "[3]", "expected_output": "False"}
                    ]
                },
                initial_code="""class Solution(object):
    def isPowerOfTwo(self, n):
        pass
"""
            ),
            
            CodeTask(
                description="""**Intersection of Two Arrays**

Даны два массива `nums1` и `nums2`, верните массив их пересечения.

Пример:
- Input: nums1 = [1,2,2,1], nums2 = [2,2]
- Output: [2]

Класс должен называться Solution, метод - intersection""",
                difficulty="easy",
                language="python",
                topic="Arrays",
                tags=["array", "hash-table"],
                test_cases={
                    "test_cases": [
                        {"input": "[[1,2,2,1], [2,2]]", "expected_output": "[2]"},
                        {"input": "[[4,9,5], [9,4,9,8,4]]", "expected_output": "[4,9]"}
                    ]
                },
                initial_code="""class Solution(object):
    def intersection(self, nums1, nums2):
        pass
"""
            ),
            
            CodeTask(
                description="""**First Unique Character in a String**

Дана строка `s`, найдите первый неповторяющийся символ и верните его индекс. Если не существует, верните -1.

Пример:
- Input: s = "leetcode"
- Output: 0

Класс должен называться Solution, метод - firstUniqChar""",
                difficulty="easy",
                language="python",
                topic="String",
                tags=["hash-table", "string"],
                test_cases={
                    "test_cases": [
                        {"input": '["leetcode"]', "expected_output": "0"},
                        {"input": '["loveleetcode"]', "expected_output": "2"},
                        {"input": '["aabb"]', "expected_output": "-1"}
                    ]
                },
                initial_code="""class Solution(object):
    def firstUniqChar(self, s):
        pass
"""
            ),
        ]
        
        # Добавляем все задачи в сессию
        session.add_all(tasks)
        await session.commit()
        
        logger.info(f"Успешно добавлено {len(tasks)} тестовых задач в БД")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации тестовых данных: {e}", exc_info=True)
        await session.rollback()
        raise
