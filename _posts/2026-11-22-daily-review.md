---
layout: post
title: "2026-11-22 코테 분석"
date: 2026-11-22 00:00:00 +0900
tags: [코테, 분석]
---

4문제를 풀었어요. 최선 0 · 개선 가능 0 · 더 쉬운 풀이 있음 0

| 문제 | 사이트 · 난이도 | 내 풀이 | 최선 | 판정 |
| --- | --- | --- | --- | --- |
| [숫자의 합](#p-11720) | 백준 Bronze IV | - | - | 분석 실패 |
| [복호화](#p-9046) | 백준 Bronze II | - | - | 분석 실패 |
| [소가 길을 건너간 이유 1](#p-14467) | 백준 Bronze I | - | - | 분석 실패 |
| [스택](#p-10828) | 백준 Silver IV | - | - | 분석 실패 |

<h2 id="p-11720">숫자의 합</h2>

[숫자의 합](https://acmicpc.net/problem/11720) · 백준 Bronze IV · Python

**분류**: 구현, 수학, 문자열  

**판정: 분석 실패** — 분석 중 오류가 나서 다음 실행에서 다시 확인이 필요해요.

- 내 풀이: -
- 최선: -

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

**판정: 분석 실패** — 분석 중 오류가 나서 다음 실행에서 다시 확인이 필요해요.

- 내 풀이: -
- 최선: -

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

**판정: 분석 실패** — 분석 중 오류가 나서 다음 실행에서 다시 확인이 필요해요.

- 내 풀이: -
- 최선: -

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

**판정: 분석 실패** — 분석 중 오류가 나서 다음 실행에서 다시 확인이 필요해요.

- 내 풀이: -
- 최선: -

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
