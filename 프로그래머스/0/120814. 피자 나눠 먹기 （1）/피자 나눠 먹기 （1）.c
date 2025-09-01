#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

int solution(int n) {
    int answer = 0;
    if (n > 7) {
      if (n % 7 > 0) {
          return answer = n / 7 + 1;
      }
     return answer = n / 7;
    } else answer = 1;
    
    return answer;
}