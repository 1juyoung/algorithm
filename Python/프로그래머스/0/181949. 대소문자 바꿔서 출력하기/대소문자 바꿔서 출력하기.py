str = input()
result = ""
for i in str:
    if i.islower() == True:
        result += i.upper()
    else:
        result += i.lower()
print(result)