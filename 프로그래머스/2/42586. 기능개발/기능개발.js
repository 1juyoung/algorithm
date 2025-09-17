function solution(progresses, speeds) {
    const days = progresses.map((p, i) =>
        Math.ceil((100 - p) / speeds[i])
    );

    const answer = [];
    let maxDay = days[0];
    let count = 1;

    for (let i = 1; i < days.length; i++) {
        if (days[i] <= maxDay) {
            // 앞 작업보다 빨리 끝나면 같이 배포
            count++;
        } else {
            // 새로운 배포 시작
            answer.push(count);
            count = 1;
            maxDay = days[i];
        }
    }
    answer.push(count);
    return answer;
}
