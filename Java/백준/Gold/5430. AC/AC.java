import java.io.*;
import java.lang.reflect.Array;
import java.util.*;

import static java.lang.System.in;
import static java.lang.System.out;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(in));
        StringBuilder answer = new StringBuilder();

        int T = Integer.parseInt(br.readLine());

        for (int i = 0; i < T; i++) {
            String RD = br.readLine();
            int n = Integer.parseInt(br.readLine());
            String arr = br.readLine();

            arr = arr.substring(1, arr.length() - 1);

            // case가 적용될 배열
            Deque<String> deque = new ArrayDeque<>();

            if (!arr.equals("")) {
                String[] arrList = arr.split(","); // 대괄호를 제거한 문자열을 배열로 변환
                for (String num : arrList) {
                    deque.offer(num); // deque에 arrList 요소들을 하나씩 저장
                }
            }

            boolean reverse = false; // case R 인지 판단
            boolean error = false;

            for (char c : RD.toCharArray()) { // 조건 문자를 array로 변환 후 하나씩 for문
                if (c == 'R') {
                    reverse = !reverse;
                } else if (c == 'D') {
                    if (deque.isEmpty()) {
                        error = true;
                        answer.append("error").append('\n');
                        break;
                    }

                    if (reverse == true) {
                        deque.pollLast();
                    } else {
                        deque.pollFirst();
                    }
                }
            }

            if (!error) {
                answer.append('[');

                while (!deque.isEmpty()) {
                    if (reverse == true) {
                        answer.append(deque.pollLast());
                    } else {
                        answer.append(deque.pollFirst());
                    }

                    if (!deque.isEmpty()) {
                        answer.append(',');
                    }
                }

                answer.append(']').append('\n');
            }
        }
        out.println(answer);
        br.close();
    }
}