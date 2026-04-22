import java.io.*;

import java.util.ArrayDeque;

import java.util.Deque;

import java.util.StringTokenizer;

import static java.lang.System.in;

import static java.lang.System.out;

public class Main {

    public static void main(String[] args) throws IOException {

        BufferedReader br = new BufferedReader(new InputStreamReader(in));

        StringBuilder sb = new StringBuilder();

        // 첫 줄 읽기

        StringTokenizer st = new StringTokenizer(br.readLine());

        int N = Integer.parseInt(st.nextToken());  // 4

        int M = Integer.parseInt(st.nextToken());  // 6

        // 미로

        int[][] miro = new int[N][M];

        int[][] dist = new int[N][M];

        /*

        for (int i = 0; i < N; i++) { // 행

            String miroText = br.readLine();

            int[] miroTexts = miroText.charAt("");

        } */

        for (int i = 0; i < N; i++) {        // 행 반복

            String miroText = br.readLine();  // "101111" 읽기

            for (int j = 0; j < M; j++) {    // 열 반복

                miro[i][j] = miroText.charAt(j) - '0';  // 한 글자씩 숫자로 변환

            }

        }

        // 미로 찾기 시작

        int[][] dir

                = {

                {-1, 0},

                {1, 0},

                {0, -1},

                {0, 1}}; // {행, 열} 위 아래 왼 오

        Deque<int[]> queue = new ArrayDeque<>();

        queue.offer(new int[]{0, 0});

        dist[0][0] = 1;

        while (!queue.isEmpty()) {

            int[] cur = queue.poll(); // 꺼내기

            int r = cur[0]; // 행

            int c = cur[1]; // 열

            for (int i = 0; i < 4; i++) {

                int nr = r + dir[i][0];

                int nc = c + dir[i][1];

                if (nr < 0 || nr >= N || nc < 0 || nc >= M) continue; // 범위 체크

                if (miro[nr][nc] == 0) continue;   // 벽 체크

                if (dist[nr][nc] != 0) continue;   // 방문 체크

                dist[nr][nc] = dist[r][c] + 1;     // 거리 저장

                queue.offer(new int[]{nr, nc});

            }

        }

        out.print(dist[N - 1][M - 1]);

        br.close();

    }

}