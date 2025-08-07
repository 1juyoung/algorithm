function solution(s) {
    const answer = [];
    const lastIndex = {};  // 각 문자의 마지막 등장 위치 저장

    for (let i = 0; i < s.length; i++) {
        const char = s[i];

        if (lastIndex[char] === undefined) {
            answer.push(-1);  // 처음 등장한 경우
        } else {
            answer.push(i - lastIndex[char]);  // 거리 계산
        }

        lastIndex[char] = i;  // 현재 위치 저장
    }

    return answer;
}

/*
문자열 s에서 글자를 순서대로 읽을 때
먼저 나온 글자가 없으면 -1
먼저 나온 글자가 있으면 해당 글자보다 몇 칸 앞에 있었는지 표시.

꺼낸 글자를 저장할 리스트 List, 현재 글자가 몇 번째 였는지 기억할 count
1. 문자열에서 글자를 하나씩 꺼내서 List 배열에 저장한다.
2. 해당 배열에 현재 글자가 없으면 -1을 나타낸다.
3. 해당 배열에서 현재 글자가 있으면
    - 현재 글자의 순서(count) - 배열에 존재한 글자 위치를 answer에 저장한다.
*/