def solution(emergency):
    answer = [0] * len(emergency)
    
    tree = {}
    # 원본을 tree라는 변수에 해시맵으로 저장 키 : 원본 숫자, 밸류 : 위치
    for idx, i in enumerate(emergency):
        tree[i] = idx
        
    # 원본 배열은 sort로 정렬
    emergency.sort(reverse=True)
    
    # 정렬된 emergency에서 하나씩 꺼내서 원본 위치를 알아낸 후 해당 위치에 순서를 집어넣음
    for idx, i in enumerate(emergency):
        answer[tree.get(i)] = idx + 1
        
    return answer