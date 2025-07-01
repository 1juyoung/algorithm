function solution(s){
    var answer = true;
    var arr = []; // 스택 추가
    s = s.split(""); // 문장 자르기
    
    for(i = 0; i < s.length; i++) {
        if (s[i] === "(") { // 열린 괄호일 경우 스택에 추가
            arr.push(s[i]);
        } 
        else if (s[0] === ")") {
            return answer = false; // 첫 번째 요소가 닫힌 괄호일 경우 answer = false
        } 
        else arr.pop(); // 그렇지 않을 경우 제거
    }
    
    if (arr.length === 0) {
        return answer = true;
    } else return answer = false;
    
    return answer;
}