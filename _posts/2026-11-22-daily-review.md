---
layout: post
title: "2026-11-22 코테 분석"
date: 2026-11-22 00:00:00 +0900
tags: [코테, 분석]
---

4문제를 풀었어요. 최선 1 · 개선 가능 3 · 더 쉬운 풀이 있음 0

| 문제 | 사이트 · 난이도 | 내 풀이 | 최선 | 판정 |
| --- | --- | --- | --- | --- |
| [숫자의 합](#p-11720) | 백준 Bronze IV | O(N) | O(N) | 최선 |
| [복호화](#p-9046) | 백준 Bronze II | O(T × L) | O(T × L) | 개선 가능 |
| [소가 길을 건너간 이유 1](#p-14467) | 백준 Bronze I | O(N) | O(N) | 개선 가능 |
| [스택](#p-10828) | 백준 Silver IV | O(N) | O(N) | 개선 가능 |

<h2 id="p-11720">숫자의 합</h2>

[숫자의 합](https://acmicpc.net/problem/11720) · 백준 Bronze IV · Python

**분류**: 구현, 수학, 문자열  

**판정: 최선** — 문자열을 순회하며 각 자릿수를 올바르게 더한 최선의 풀이입니다.

- 내 풀이: O(N) - 문자열의 길이 N만큼 순회하며 각 문자를 숫자로 변환하여 더하기 때문입니다.
- 최선: O(N) - 입력된 N개의 숫자를 모두 확인해야 하므로 최소 N번의 연산이 필요합니다.

**잘한 점**

- 문자열을 그대로 순회하면서 각 문자를 정수로 변환해 더하는 직관적인 접근을 사용했습니다.
- 불필요한 복잡한 자료구조나 알고리즘을 사용하지 않고 간결하게 작성했습니다.

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

**판정: 개선 가능** — 딕셔너리를 이용해 빈도수를 잘 세었으나 파이썬 내장 모듈(Counter) 및 불필요한 코드를 개선할 수 있습니다.

- 내 풀이: O(T × L) (각 테스트 케이스마다 길이 L인 문자열을 순회하며 빈도수를 계산하므로 문자열 길이에 비례함)
- 최선: O(T × L) (모든 문자의 빈도수를 확인하기 위해 입력 문자열 전체를 한 번씩 순회해야 함)

**잘한 점**

- dict.get() 기법을 활용해 문자의 등장 횟수를 깔끔하게 집계했습니다.
- 가장 높은 빈도수가 2개 이상일 때 '?'를 출력하는 조건을 정확하게 구현했습니다.

**고칠 점**

- input()은 이미 문자열을 반환하므로 str(input()) 형태의 불필요한 형변환은 제거하는 것이 좋습니다.
- 딕셔너리 변수명 tree는 해시 맵/빈도수 집계 자료구조의 목적에 맞지 않으므로 counts 또는 freq 같은 명확한 이름을 추천합니다.
- collections 모듈의 Counter 클래스를 활용하면 빈도수 집계와 최다 빈도 문자 추출을 더욱 간결하게 처리할 수 있습니다.

**더 나은 풀이**

```python
from collections import Counter

t = int(input())
for _ in range(t):
    s = input().replace(' ', '')
    counter = Counter(s)
    most = counter.most_common(2)
    if len(most) > 1 and most[0][1] == most[1][1]:
        print('?')
    else:
        print(most[0][0])
```

collections.Counter의 most_common(2)를 사용하면 가장 많이 등장한 알파벳 상위 2개를 가져올 수 있습니다. 이를 통해 1등과 2등의 빈도수가 같은지만 비교하면 되므로 로직이 매우 단순해집니다.

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

**판정: 개선 가능** — 문제 풀이 로직은 정확하지만, 입력을 배열에 저장하지 않고 즉시 처리하면 코드를 훨씬 간결하게 개선할 수 있습니다.

- 내 풀이: O(N) - N개의 관찰 기록을 리스트에 저장한 뒤 다시 순회하므로 O(N) 시간이 소요됩니다.
- 최선: O(N) - N개의 관찰 데이터를 한 번씩 확인해야 하므로 O(N)이 최선입니다.

**잘한 점**

- 소의 번호를 키(Key), 위치를 값(Value)으로 저장하기 위해 딕셔너리를 활용한 접근이 훌륭합니다.
- 소의 이전 위치와 현재 위치를 비교하여 위치가 바뀌었을 때 정확하게 횟수를 누적했습니다.

**고칠 점**

- 입력을 nums 리스트에 모두 저장을 해둔 뒤 다시 반복문을 돌릴 필요 없이, 입력을 받는 즉시 딕셔너리를 확인하고 갱신하면 코드와 메모리를 아낄 수 있습니다.
- split(" ")보다는 split()을 사용하는 것이 공백이 여러 개 섞여 들어오는 예외 상황 처리에 더 안전합니다.
- tree.get(k) == None보다는 k not in tree 형태의 파이썬 키워드를 활용하는 것이 가독성이 좋아집니다.

**더 나은 풀이**

```python
n = int(input())
pos = {}
count = 0

for _ in range(n):
    cow, location = map(int, input().split())
    if cow in pos and pos[cow] != location:
        count += 1
    pos[cow] = location

print(count)
```

입력을 받음과 동시에 기존 위치와 비교하여 이동 횟수를 계산하므로, 별도의 입력 리스트(nums)가 필요 없습니다. 매 반복마다 pos[cow] = location으로 위치를 갱신해 주면 획기적으로 조건문을 줄일 수 있습니다.

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

**판정: 개선 가능** — 스택의 기본 동작은 정확히 구현했으나, 입력 데이터를 전체 저장하는 방식과 입출력 속도 측면에서 개선할 점이 있습니다.

- 내 풀이: O(N) - N개의 명령을 리스트에 저장하고 순회하며 스택 연산을 수행하므로 O(N)입니다.
- 최선: O(N) - N개의 명령어를 각각 O(1) 연산으로 처리하여 전체 O(N)에 해결하는 것이 최선입니다.

**잘한 점**

- 파이썬 리스트의 append와 pop을 활용하여 스택 구조를 바르게 구현했습니다.
- 스택이 비어있는 경우(-1 출력)에 대한 조건 처리를 정확히 작성했습니다.

**고칠 점**

- sys.stdin.readline을 사용하면 입출력 속도를 대폭 개선할 수 있습니다.
- 모든 입력 명령을 미리 리스트 l에 전부 저장한 뒤 처리하면 불필요한 메모리가 사용되므로, 입력 받는 즉시 처리하는 것이 좋습니다.
- input().split(" ") 대신 공백 문자를 자동으로 처리해 주는 input().split()을 사용하는 것이 좋습니다.

**더 나은 풀이**

```python
import sys

input = sys.stdin.readline
n = int(input())
stack = []

for _ in range(n):
    cmd = input().split()
    if cmd[0] == 'push':
        stack.append(cmd[1])
    elif cmd[0] == 'pop':
        print(stack.pop() if stack else -1)
    elif cmd[0] == 'size':
        print(len(stack))
    elif cmd[0] == 'empty':
        print(0 if stack else 1)
    elif cmd[0] == 'top':
        print(stack[-1] if stack else -1)
```

sys.stdin.readline을 사용하여 입력 속도를 크게 줄였습니다. 또한 명령을 미리 배열에 다 담지 않고 입력받는 즉시 처리하여 메모리를 아꼈고, 삼항 연산자를 사용해 코드를 한결 간결하게 만들었습니다.

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
