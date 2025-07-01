function solution(s) {
    var answer = "";
    let numbers = [];
    s = s.split(" ");
    numbers = s.map(num => parseInt(num));
    numbers = numbers.sort((a, b) => a - b);
    answer = answer.concat(numbers[0], " ", numbers[s.length-1])
    return answer.toString();
}