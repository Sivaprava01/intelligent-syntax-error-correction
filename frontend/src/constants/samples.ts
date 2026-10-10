export interface SampleProgram {
  id: string;
  name: string;
  description: string;
  code: string;
}

export const SAMPLE_PROGRAMS: SampleProgram[] = [
  {
    id: 'sample-1',
    name: '1. Missing Semicolons & Variables',
    description: 'Declaration missing semicolon before return statement',
    code: `#include <stdio.h>

int main() {
    int a = 10
    int b = 20;
    int sum = a + b;
    printf("Sum is: %d\\n", sum);
    return 0;
}`,
  },
  {
    id: 'sample-2',
    name: '2. Unclosed Block & Loop Syntax',
    description: 'For-loop syntax and missing closing brace',
    code: `int compute_factorial(int n) {
    int result = 1;
    for (int i = 1; i <= n; i++) {
        result = result * i;
    }
    return result;
`,
  },
  {
    id: 'sample-3',
    name: '3. Missing Parenthesis in If Condition',
    description: 'Conditional expression missing closing parenthesis',
    code: `int max_value(int a, int b) {
    if (a > b {
        return a;
    } else {
        return b;
    }
}`,
  },
  {
    id: 'sample-4',
    name: '4. Clean Valid C Program',
    description: 'Fully conforming syntax with functions and loops',
    code: `int multiply(int x, int y) {
    return x * y;
}

int main() {
    int num1 = 5;
    int num2 = 12;
    int product = multiply(num1, num2);
    return product;
}`,
  },
];
