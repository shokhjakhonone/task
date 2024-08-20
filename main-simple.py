def main(input: str) -> str:
    try:
        a, operator, b = input.split()
        a = int(a)
        b = int(b)
        
        if operator == '+':
            result = a + b
            graph = '+' * result
        elif operator == '-':
            result = a - b
            graph = '-' * result
        elif operator == '*':
            result = a * b
            graph = '*' * result
        elif operator == '/':
            result = a // b
            graph = '/' * result
        else:
            raise ValueError("Invalid operator")
        
        return str(result), graph
    except ValueError:
        return "Invalid input. Пожалуйста, добавьте пробел между числами и оператором."

# Пример использования
input_str = input("Введите арифметическое выражение: ")
result_str, graph_str = main(input_str)


print("Результат:", result_str)
