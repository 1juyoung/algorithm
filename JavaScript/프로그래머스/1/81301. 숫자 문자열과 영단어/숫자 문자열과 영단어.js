function solution(s) {
    const words = ["zero","one","two","three","four","five","six","seven","eight","nine"];
    
    for (let i = 0; i < words.length; i++) {
        s = s.replaceAll(words[i], i);
    }
    
    return Number(s);
}
