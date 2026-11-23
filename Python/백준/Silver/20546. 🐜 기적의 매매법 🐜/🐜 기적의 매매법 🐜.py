n = int(input())
nums = list(map(int, input().split()))

answer = [0, 0]

anStr = ''
# 연속 3번 하락 또는 상승인지 카운트할 애
count = {-1: 0, 1: 0}

# 여기서 키 0의 값은 현금을 말함
# 다른 숫자는 매입한 값과 매수의 양
jh = {0: n}
sm = {0: n}

for idx, i in enumerate(nums):

    if idx != 0:
        if nums[idx - 1] < i:
            count[1] += 1
            count[-1] = 0
        elif nums[idx - 1] > i:
            count[-1] += 1
            count[1] = 0
        else:
            count[-1] = 0
            count[1] = 0

    if i <= n:
        while jh[0] >= i:
            jh[0] = jh[0] - i
            jh[i] = jh.get(i, 0) + 1

    if count[-1] >= 3:
        if i <= sm[0]:
            while sm[0] >= i:
                sm[0] = sm[0] - i
                sm[i] = sm.get(i, 0) + 1

    if count[1] >= 3:
        for j in sm.keys():
            if j == 0:
                continue
            sm[0] = sm[0] + (i * sm[j])
            sm[j] = 0

for a, k in sm.items():
    if a != 0:
        answer[0] += k * nums[-1]

for l, q in jh.items():
    if l != 0:
        answer[1] += q * nums[-1]
# sm
answer[0] = answer[0] + sm[0]

# jh
answer[1] = answer[1] + jh[0]

if answer[0] > answer[1]:
    anStr = "TIMING"
elif answer[0] < answer[1]:
    anStr = "BNP"
else:
    anStr = "SAMESAME"

print(anStr)
