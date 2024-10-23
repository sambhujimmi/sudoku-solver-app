import numpy as np

sudoku = [[3, 0, 1, 6, 7, 2, 0, 8, 4],
          [0, 0, 0, 8, 0, 1, 2, 0, 7],
          [0, 8, 7, 0, 0, 0, 6, 1, 0],
          [0, 9, 2, 0, 0, 5, 3, 7, 8],
          [8, 0, 0, 7, 0, 0, 0, 0, 0],
          [0, 0, 4, 9, 2, 0, 5, 0, 0],
          [1, 0, 0, 0, 0, 6, 0, 0, 5],
          [0, 0, 6, 0, 5, 0, 8, 0, 0],
          [5, 7, 3, 2, 0, 4, 0, 0, 0]]

n = 9
m = 3

def check(sudoku, row, col, val):
    # row and col
    for i in range(n):
        if sudoku[row][i] == val or sudoku[i][col] == val:
            return False
    # box
    boxrow = (row//m)*m
    boxcol = (col//m)*m
    for i in range(boxrow, m):
        for j in range(boxcol, m):
            if sudoku[i][j] == val:
                return False
    return True

def possibles(sudoku, i, j):
    possible_nums = []
    for v in range(n+1):
        if check(sudoku, i, j, v):
            possible_nums.append(v)
    return possible_nums

def solver(sudoku):
    empty = {}
    for i in range(n):
        for j in range(n):
            if sudoku[i][j] == 0:
                possible_nums = possibles(sudoku, i, j)
                if len(possible_nums) < 1:
                    print("Impossible to solve")
                    print(possible_nums)
                    print(i, j)
                elif len(possible_nums) == 1:
                    sudoku[i][j] = possible_nums[0]
                else:
                    empty[(i, j)] = possible_nums
    # backtracking
    pos = [x for x in empty]
    print(pos)
    i = 0
    while i < len(pos):
        row = pos[i][0]
        col = pos[i][1]
        val = sudoku[row][col]
        possible_nums = empty[pos[i]]
        if val == 0:
            num = possible_nums[0]
        elif val == possible_nums[-1]:
            i -= 1
            continue
        else:
            num = possible_nums[possible_nums.index(val)+1]
        sudoku[row][col] = num
        if check(sudoku, row, col, num):
            i += 1
    return sudoku

print(sudoku)
print(solver(sudoku))