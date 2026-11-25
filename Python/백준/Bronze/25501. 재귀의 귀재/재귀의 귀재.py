count = 0

def recursion(s, l, r):
    global count
    count += 1
    if l >= r:
        return print(f'1 {count}')
    elif s[l] != s[r]:
        return print(f'0 {count}')
    else:
        return recursion(s, l + 1, r - 1)


def isPalindrome(s):
    return recursion(s, 0, len(s) - 1)

n = int(input())  # 테스트 케이스 개수

for i in range(n):
    count = 0
    st = input()
    isPalindrome(st)