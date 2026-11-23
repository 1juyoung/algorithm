---
layout: post
title: "2026-11-22 코테 분석"
date: 2026-11-22 00:00:00 +0900
tags: [코테, 분석]
---

4문제를 풀었어요. 최선 0 · 개선 가능 4 · 더 쉬운 풀이 있음 0

| 문제 | 사이트 · 난이도 | 내 풀이 | 최선 | 판정 |
| --- | --- | --- | --- | --- |
| [숫자의 합](#p-11720) | 백준 Bronze IV | O(N) | O(N) | 개선 가능 |
| [복호화](#p-9046) | 백준 Bronze II | O(T | O(T | 개선 가능 |
| [소가 길을 건너간 이유 1](#p-14467) | 백준 Bronze I | O(N) | O(N) | 개선 가능 |
| [스택](#p-10828) | 백준 Silver IV | O(N) | O(N) | 개선 가능 |

<h2 id="p-11720">숫자의 합</h2>

[숫자의 합](https://acmicpc.net/problem/11720) · 백준 Bronze IV · Python

**분류**: 구현, 수학, 문자열  

**판정: 개선 가능** — 정답이지만 불필요한 형변환과 사용하지 않는 변수가 있으며, 내장 함수를 활용해 더 간결하게 작성할 수 있습니다.

- 내 풀이: O(N) - N개의 숫자를 순회하면서 각 문자를 정수로 변환하여 합산합니다.
- 최선: O(N) - N개의 숫자를 모두 읽어야 하므로 O(N)이 최선의 시간 복잡도입니다.

**잘한 점**

- 문자열을 한 글자씩 순회하며 정수로 변환해 더하는 직관적인 접근입니다.
- 입력 크기(N <= 100)에 적합한 O(N) 시간 복잡도로 올바르게 구현했습니다.

**고칠 점**

- input()은 이미 문자열을 반환하므로 str(input())과 같이 불필요하게 str()로 감쌀 필요가 없습니다.
- 첫째 줄의 n 변수가 실제 로직에서 사용되지 않습니다.
- Python의 내장 함수 sum()과 map()을 사용하면 반복문 없이 한 줄로 깔끔하게 처리할 수 있습니다.

**더 나은 풀이**

```python
input()
print(sum(map(int, input())))
```

input()으로 읽어온 숫자 문자열의 각 글자를 map(int, ...)을 통해 정수로 바꾸고 sum()으로 모두 합쳤습니다. 불필요한 변수 선언과 반복문을 제거하여 코드가 매우 직관적이고 간결해집니다.

<details markdown="1">
<summary>내 코드 보기</summary>

```python
n = int(input())
nums = str(input())
answer = 0
for i in nums:
    answer += int(i)
print(answer)
```

</details>

<h2 id="p-9046">복호화</h2>

[복호화](https://acmicpc.net/problem/9046) · 백준 Bronze II · Python

**분류**: 구현, 문자열  

**판정: 개선 가능** — 딕셔너리를 활용해 빈도수를 정확히 계산했으나, 불필요한 함수 호출과 변수명 개선 및 파이썬 내장 모듈 활용 여지가 있습니다.

- 내 풀이: O(T × L) - 각 테스트 케이스마다 길이 L인 문자열을 순회하며 딕셔너리에 빈도수를 저장하고 탐색합니다.
- 최선: O(T × L) - 테스트 케이스 T개에 대해 각 문장의 길이 L만큼 확인해야 하므로 O(T × L)이 최선입니다.

**잘한 점**

- dict.get() 메서드를 활용해 문자 빈도수를 안전하게 카운팅했습니다.
- 가장 많이 등장한 문자의 빈도수가 중복될 때 '?'를 출력하는 조건을 올바르게 작성했습니다.

**고칠 점**

- str(input())에서 input()은 이미 문자열을 반환하므로 불필요한 str() 형변환입니다.
- 변수명 'tree'는 딕셔너리 카운터 역할을 하므로 'freq'나 'counts' 같은 명확한 이름을 사용하는 것이 좋습니다.
- collections.Counter 모듈의 most_common() 메서드를 활용하면 최다 빈도 문자 탐색 및 최댓값 중복 검사를 훨씬 단순하게 구현할 수 있습니다.

**더 나은 풀이**

```python
import sys
from collections import Counter

def main():
    input = sys.stdin.readline
    t = int(input())
    
    for _ in range(t):
        text = input().rstrip().replace(' ', '')
        counter = Counter(text)
        most_common = counter.most_common(2)
        
        if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
            print('?')
        else:
            print(most_common[0][0])

if __name__ == '__main__':
    main()
```

collections.Counter의 most_common(2) 함수를 활용하면 가장 빈도수가 높은 상위 2개 문자만 뽑아서 빈도수가 같은지 바로 비교할 수 있습니다. 이를 통해 코드가 훨씬 짧아지고 직관적으로 변경됩니다.

<details markdown="1">
<summary>내 코드 보기</summary>

```python
n = int(input())

for o in range(n):
    tree = {}
    
    word = str(input())
    
    for i in word:
        if i == ' ':
            continue
        tree[i] = tree.get(i, 0) + 1

    nums = list(tree.values())
    maxN = max(tree.values())
    
    if nums.count(maxN) > 1:
        print('?')
        
    else:
        for j, k in tree.items():
            if k == maxN:
                  print(j)
```

</details>

<h2 id="p-14467">소가 길을 건너간 이유 1</h2>

[소가 길을 건너간 이유 1](https://acmicpc.net/problem/14467) · 백준 Bronze I · Python

**분류**: 구현  

**판정: 개선 가능** — 딕셔너리를 이용한 위치 추적 접근은 훌륭하나, 불필요한 배열 저장과 입력 처리 및 조건문 구조에서 개선할 부분이 있습니다.

- 내 풀이: O(N) - 관찰 횟수 N만큼 입력을 리스트에 저장한 뒤 순회하여 딕셔너리를 조회하므로 O(N)입니다.
- 최선: O(N) - N개의 관찰 기록을 최소 한 번씩 확인해야 하므로 O(N)이 최선입니다.

**잘한 점**

- 딕셔너리(해시 맵)를 활용하여 소의 이전 위치를 빠르게 탐색하도록 작성했습니다.
- 카운트 변수(count)를 잘 활용하여 문제 요구사항에 맞게 이동 횟수를 집계했습니다.

**고칠 점**

- input().split(" ") 대신 공백이 여러 개 섞여 있어도 안정적으로 분리해 주는 input().split()을 사용하는 것이 좋습니다.
- 입력값을 배열에 모두 저장한 후 다시 반복문을 돌기보다는, 입력을 받는 즉시 판별하면 메모리와 시간 모두 절약됩니다.
- == None 비교 대신 is None을 사용하거나 if cow in tree 형태의 표준적인 키 검사 방식을 사용하는 것이 가독성에 유리합니다.

**더 나은 풀이**

```python
n = int(input())
pos = {}
count = 0

for _ in range(n):
    cow, p = map(int, input().split())
    if cow in pos and pos[cow] != p:
        count += 1
    pos[cow] = p

print(count)
```

입력을 받는 반복문 하나에서 위치 변동을 즉시 처리하도록 단순화했습니다. 이미 기록된 소의 위치와 현재 위치가 다를 때만 카운트를 올리고 갱신함으로써 조건문을 훨씬 간결하게 만들었습니다.

<details markdown="1">
<summary>내 코드 보기</summary>

```python
n = int(input())
tree = {}
nums = []
count = 0
for o in range(n):
    nums.append(list(map(int, input().split(" "))))
for k, y in nums:
    if tree.get(k) == None:
        tree[k] = y
        
    if tree.get(k) != y:
        count += 1
        tree[k] = y

print(count)
```

</details>

<h2 id="p-10828">스택</h2>

[스택](https://acmicpc.net/problem/10828) · 백준 Silver IV · Python

**분류**: 자료 구조, 구현, 스택  

**판정: 개선 가능** — 스택의 기능을 올바르게 구현했으나, 입력을 전처리하여 메모리에 미리 저장하는 과정과 입출력 속도 면에서 개선할 수 있습니다.

- 내 풀이: O(N) - N개의 명령을 입력받아 리스트에 저장한 뒤 하나씩 처리하므로 O(N)의 시간 복잡도를 가집니다.
- 최선: O(N) - N개의 명령에 대해 스택 연산을 각각 O(1) 시간에 수행하므로 최선의 시간 복잡도는 O(N)입니다.

**잘한 점**

- 파이썬의 리스트를 활용하여 스택 연산(push, pop, top 등)의 핵심 동작을 올바르게 구현했습니다.
- 빈 스택에서 pop이나 top을 호출할 때 예외 처리를 꼼꼼하게 처리하였습니다.

**고칠 점**

- 입력을 받는 즉시 처리하지 않고 리스트 `l`에 모두 저장하여 불필요한 메모리를 사용하고 입력을 두 번 순회합니다.
- `input().split()`은 이미 문자열 리스트를 반환하므로 `list(map(str, ...))` 구문은 중복적이고 불필요합니다.
- `split(" ")` 대신 `split()`을 사용해야 연속된 공백이나 줄바꿈 처리 시 안전합니다.
- 반복적인 입력 처리를 위해 `sys.stdin.readline`을 사용하면 실행 시간을 대폭 줄일 수 있습니다.

**더 나은 풀이**

```python
import sys

input = sys.stdin.readline

n = int(input())
stack = []

for _ in range(n):
    command = input().split()
    cmd = command[0]
    
    if cmd == 'push':
        stack.append(command[1])
    elif cmd == 'pop':
        print(stack.pop() if stack else -1)
    elif cmd == 'size':
        print(len(stack))
    elif cmd == 'empty':
        print(0 if stack else 1)
    elif cmd == 'top':
        print(stack[-1] if stack else -1)
```

sys.stdin.readline을 사용하여 입출력 속도를 대폭 개선하였습니다. 명령어를 입력받는 즉시 처리하여 불필요한 리스트 생성 및 메모리 낭비를 방지하고, 삼항 연산자로 가독성을 높였습니다.

<details markdown="1">
<summary>내 코드 보기</summary>

```python
n = int(input())
l = []
for i in range(n):
    l.append(list(map(str, input().split(" "))))

s = []

for i in range(len(l)):
    if l[i][0] == 'push':
        s.append(l[i][1])
    elif l[i][0] == 'pop':
        if len(s) == 0:
            print(-1)
        else:
            print(s.pop())
    elif l[i][0] == 'size':
        print(len(s))
    elif l[i][0] == 'empty':
        if len(s) == 0:
            print(1)
        else:
            print(0)
    else:
        if len(s) == 0:
            print(-1)
        else:
            print(s[-1])
```

</details>
