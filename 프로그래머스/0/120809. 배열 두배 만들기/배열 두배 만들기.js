function solution(numbers) {
    var answer = [];
    for (a of numbers) {
        a = a * 2;
        answer.push(a);
    }
    return answer;
}