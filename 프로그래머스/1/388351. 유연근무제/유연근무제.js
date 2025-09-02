function toMinutes(t) {
  const h = Math.floor(t / 100);
  const m = t % 100;
  return h * 60 + m;
}

function solution(schedules, timelogs, startday) {
  let answer = 0;
  const n = schedules.length; // 직원 수

  for (let i = 0; i < n; i++) {
    const hope = toMinutes(schedules[i]);
    let ok = true;

    for (let d = 0; d < 7; d++) {
      const dayOfWeek = (startday - 1 + d) % 7;
      if (dayOfWeek >= 5) continue; // 주말 제외

      const actual = toMinutes(timelogs[i][d]);
      if (actual > hope + 10) {
        ok = false;
        break;
      }
    }

    if (ok) answer++;
  }
  return answer;
}
