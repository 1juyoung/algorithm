function solution(str1, str2) {
    var answer = '';
    const answerArr = [];
    const str1Arr = [...str1];
    const str2Arr = [...str2];
    
    for(i = 0; i < str2Arr.length; i++) {
        answerArr.push(str1Arr[i]);
        answerArr.push(str2Arr[i]);
    }
    
    return answerArr.join('');
}