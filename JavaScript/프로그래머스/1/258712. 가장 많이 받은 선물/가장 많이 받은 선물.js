function solution(friends, gifts) {

    const giftGivenCount = {};  // 친구별로 준 선물 수
    const giftReceivedCount = {}; // 친구별로 받은 선물 수
    const pairCount = {};  // 두 사람간 준 선물 수 기록

    friends.forEach(f => {
        giftGivenCount[f] = 0;
        giftReceivedCount[f] = 0;
    });


    gifts.forEach(record => {
        const [giver, receiver] = record.split(" ");

        // 친구별 선물 기록 집계
        giftGivenCount[giver]++;
        giftReceivedCount[receiver]++;

        // 두 사람 간 선물 주고받은 횟수 기록
        const key = `${giver}|${receiver}`;
        pairCount[key] = (pairCount[key] || 0) + 1;
    });

    // 선물 지수 계산
    const giftScore = {};
    friends.forEach(f => {
        giftScore[f] = giftGivenCount[f] - giftReceivedCount[f];
    });

    const nextMonthReceive = {};
    friends.forEach(f => {
        nextMonthReceive[f] = 0;
    });

    // 선물 받을 사람 계산
    for (let i = 0; i < friends.length; i++) {
        for (let j = i + 1; j < friends.length; j++) {
            const A = friends[i];
            const B = friends[j];

            const AtoB = pairCount[`${A}|${B}`] || 0;
            const BtoA = pairCount[`${B}|${A}`] || 0;

            if (AtoB > BtoA) {
                // A가 B보다 많이 줬으면 A가 선물 1개 받음
                nextMonthReceive[A]++;
            } else if (BtoA > AtoB) {
                // B가 A보다 많이 줬으면 B가 선물 1개 받음
                nextMonthReceive[B]++;
            } else {
                // 주고받은 기록 없거나 같을 경우 선물 지수 비교
                if (giftScore[A] > giftScore[B]) {
                    nextMonthReceive[A]++;
                } else if (giftScore[B] > giftScore[A]) {
                    nextMonthReceive[B]++;
                }
                // 같으면 아무도 선물 안 받음
            }
        }
    }

    // 가장 많이 받을 친구의 선물 수
    return Math.max(...Object.values(nextMonthReceive));
}

/*
선물 개수가 다르다면, 선물 많이 준 사람이 적게 준 사람한테 다음 달에 선물 받음
두사람 중 주고받은 기록이 없거나 수가 같으면 선물지수가 더 큰 사람이 다음 달에 선물을 받음.
만약 선물지수도 같으면 선물을 주고 받지 않음.

선물 지수는 이번 달까지 자신이 친구들에게 준 선물의 수에서 받은 선물의 수를 뺀 값

선물을 가장 많이 받을 친구가 받을 선물의 수를 알고 싶다.
친구의 이름 문자열 배열, 이번달까지 친구들이 주고받은 선물 기록을 담은 문자열 배열 gifts
"선물을 준 친구이름 선물을 받은 친구 이름"
이 때 다음 달에 가장많은 선물을 받는 친구가 받을 선물의 수를 return하도록 
*/