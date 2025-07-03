function solution(arr)
{
    var answer = [];
    var array = [];
    for (i = 0; i < arr.length; i++) {
        if (arr[i] !== arr[i + 1]) {
            answer.push(arr[i]);
        } else array.push();
    }
    
    return answer;
}

/*
배열 arr의 각 원소는 0-9
연속적으로 나타나는 숫자는 하나만 남기고 전부 제거.
*/