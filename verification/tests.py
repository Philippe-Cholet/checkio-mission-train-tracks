from itertools import chain
from re import findall

PATTERN = r'(\d+)x(\d+):([^,]+),([S0-9,]+)'
TABLE = {
    '3': 'NE',
    '5': 'WE',
    '6': 'NW',
    '9': 'SE',
    'A': 'NS',
    'C': 'SW',
}

SPECS = '''
8x8:x6nAl5iCa,4,2,2,3,4,5,S6,3,4,6,5,S3,1,3,3,4
8x8:j5c6i5zhCd,3,6,7,S5,4,3,6,6,8,7,7,S5,5,3,2,3
10x8:m3p6n3j9qAc5a,3,2,3,4,S6,6,5,5,5,2,6,7,5,S6,4,3,6,4
10x10:j6s9nCpCa95q5k9d,5,4,7,8,7,S6,7,4,4,8,6,S5,7,7,5,7,7,8,5,3
15x10:kCc6jAf5d95kCrCa5h9p6zn9j,2,1,3,1,S2,4,6,4,4,5,6,6,3,3,3,6,S5,11,7,8,6,5,1,2,2
15x15:g9Cf3zcAb9a3a3h9CzaAzy5Cs5a5c6d56fCzh9g,10,10,9,11,7,5,5,S6,9,7,4,4,2,2,2,9,6,8,7,4,4,4,3,6,14,8,S8,6,4,2
10x20:p6gAe5d9f9bAyCn6dCi3gAhCzc3g5d3x6jCb,5,12,7,7,9,15,13,S12,5,7,3,3,3,S5,7,5,7,5,7,6,4,3,5,9,3,4,6,2,2,3
10x20:j6d6b9c9e3sAm6cChCc6g3c363e6m9kAaAnAc6gCk5s5i9c,8,10,11,10,11,14,S11,10,11,9,7,S7,5,6,3,5,7,9,10,8,3,5,5,6,4,3,4,3,3,2
15x25:5kChAa3Cg3i5Cx6c5e5b5p5d56k3eCf5e9dCbCfAaCf3l3h6o9mAqAc5j3aAwAb3oCn6l3zs9k,10,12,17,S18,17,8,13,11,11,12,15,11,9,7,3,S9,9,10,9,10,9,13,8,10,14,10,7,5,5,6,6,5,5,5,7,3,3,2,2,2
20x20:i5b5e5jCq6f3rAcAAuCg3lAk6hAfCp9b3cCl3rAd96m36uA35zzi3qAd5p9o3w5aAe,4,5,5,3,3,6,7,7,10,17,12,12,12,13,S8,5,4,5,4,3,15,11,9,4,8,S9,8,9,12,8,7,6,4,2,3,8,5,6,7,4
30x30:rCs3Ca6iCo3aAa5tAzi5mAg6dAzc6Azu6v9cAc5w5zg5z6d9zeCz3u6d3zg9zzy9h6b3s6y3i3a9a3q3zzzl3zbCzeCAb6zy6x9w,6,3,5,5,3,4,S8,6,6,6,6,9,4,11,8,10,8,11,10,10,5,12,13,7,11,12,9,5,3,3,14,14,16,10,13,S8,4,7,7,7,10,7,9,8,6,4,3,3,7,8,9,7,4,5,5,7,7,3,5,2
45x35:i5zi6c5Ca3b5zt5bCzi5555e3zl5zn3C3zqAb5zn6c9b9zs95zg69d5zu3h9xAv556zs5t5m6zbAa5pAzwAb5zh3b5a9bAeCzzzoCzzzzzbAzl9fAzk6c9bAa3zoAzu3c6zi9g9zzzzzzrCc36zg3g9fAzi5d5a3zzzkAa6,2,7,8,7,12,8,7,8,9,9,9,7,7,6,6,5,10,3,2,1,5,5,4,3,5,7,6,6,8,11,10,4,11,10,14,13,8,7,7,4,7,6,S8,7,7,10,S10,11,11,8,8,8,11,9,14,10,13,10,9,8,13,13,6,4,3,1,3,6,10,12,13,9,3,10,14,17,12,11,3,3
40x40:e5a9zf3aA3mCzdAze5cAi3zkAzdAm5zh5aAa55zzzzzz5zn5zzzbCzk3a3aAzzw9dAzzzzl5zk9CbCzg5aAfCzk6zg3c5bCa6zfCdAzi9zk3zzyCa5i6zfCdCl35y6c9b3d6y3bAgAc96p3zzdAzzzzoChCzb3c3c9zm3zfAj,3,4,5,5,7,3,2,2,5,4,2,9,13,16,24,27,29,18,12,7,6,7,8,11,5,1,3,1,4,S6,7,6,6,4,5,6,7,9,4,3,10,12,11,S13,12,10,10,3,1,2,3,4,5,4,5,5,4,6,3,7,6,12,9,10,4,10,6,7,12,11,17,13,15,7,3,5,11,10,5,3
50x50:a5zxCzxAhAzk5i3zq5hCzk9zy3f36zuAzzb5zs6e5zlCa69dAa5zm6zuAg5zzzzzzzp6zx3zzzzfCzu3zx9zzzzzs5s9zc55zzn3dAzcCkAa6zg3wCzbAzr9b5aAzzp6aAAzk3bAdCzyCx6a5c5e6pAwCuCcAt3f9tCzeAq3za6c6zzzzmAzAzzcAo3zyAx5hCbCa63bCznAd5bCzvCb3c5y3CaAzwAj555zj3a9s3a,3,6,6,14,7,5,6,4,5,11,10,13,13,7,4,4,3,5,1,3,11,11,17,16,10,15,7,8,S6,8,8,5,3,5,5,3,12,11,13,8,6,8,5,7,12,9,9,9,13,13,4,6,6,S6,6,10,8,7,10,13,15,8,8,3,1,3,3,7,1,6,3,2,3,1,8,9,10,7,8,4,11,13,14,10,19,13,13,10,6,4,3,5,5,7,17,13,20,15,13,6
50x50:zf9zy3fAzn9zzfCzw3zm9l3zh9Czq9b9sCzg3zq3b6rCzCv36yA3zt9zwAzCzrAzAa3zzzzzs6r5zbArAzb9CaAdCm9xCcAt6s9b6e6yAk5CaAm6zc6c6b3hAe95g9b55eCl9k356f63bCe9rAzd3a95i3y96aCAzuCAa9t3Czzt3za6zaAvCzw6zg5zy5zpAaCcCzzdCf3zbArAb5cC9za3p5zpCc55zeCpCh3c3Czzo9zd6zkAd3d3zrCa5zrCzzzzzzzCh,4,5,1,3,8,13,17,13,12,12,7,9,7,6,7,5,6,7,5,6,4,11,10,12,10,12,5,10,5,9,9,10,13,13,6,8,10,16,14,9,14,S16,14,8,12,11,14,5,5,6,8,7,4,4,5,6,6,11,9,9,8,5,5,7,10,4,2,6,10,9,11,15,12,19,24,22,22,13,8,9,5,6,7,10,7,6,8,S10,15,15,13,8,10,7,9,12,7,5,1,3
'''

GROUPS = findall(PATTERN, SPECS)


def define_input(ncols, nrows, line, S_counts):
    ncols, nrows = int(ncols), int(nrows)
    S_counts = S_counts.split(',')
    columns, rows = S_counts[:ncols], S_counts[ncols:]
    xA, yB = (next(i for i, item in enumerate(lst) if 'S' in item)
              for lst in (rows, columns))
    yA, xB = 0, nrows - 1
    start, end = (xA, yA), (xB, yB)

    columns = [int(s.replace('S', '')) for s in columns]
    rows = [int(s.replace('S', '')) for s in rows]

    line = chain.from_iterable([TABLE[s]] if s in TABLE else
                               [''] * (ord(s) - ord('a') + 1)
                               for s in line)
    grid = [[next(line) for _ in range(ncols)] for _ in range(nrows)]
    grid[xA][yA] = grid[xA][yA].replace('W', '')
    grid[xB][yB] = grid[xB][yB].replace('S', '')

    constraints = {(i, j): set(dirs) for i, row in enumerate(grid)
                   for j, dirs in enumerate(row) if dirs}
    return rows, columns, start, end, str(constraints)
    # JSON does not accept tuples as dict keys. So str(dict) instead.


TESTS = {'Basic': [], 'Extra': []}

for n, groups in enumerate(GROUPS):
    category = ('Basic', 'Extra')[n >= 4]
    in_data = define_input(*groups)
    TESTS[category].append({'input': in_data, 'answer': in_data})


if __name__ == '__main__':
    REAL_INPUTS = []
    for tests in TESTS.values():
        for test in tests:
            *ints, constraints = test['input']
            REAL_INPUTS.append((*ints, eval(constraints)))

    # For "editor/initial_code/python_3"
    print(tuple(REAL_INPUTS[:4]))

    # For info/task_description.html
    specs = SPECS.strip().splitlines()
    url = 'https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/tracks.html'
    for ntest, (spec, (ncols, nrows, *_)) in enumerate(zip(specs, GROUPS), 1):
        title = f'{nrows} rows, {ncols} columns'
        print(f'    <a href="{url}#{spec}" title="{title}">{ntest}</a>')


# def solution_from_copy():
#     # Solve the game with the Tatham's executable, copy the solution with it,
#     # call this function & you have the string of directions copied instead.
#     import pyperclip
#     text = pyperclip.paste()
#     MOVES = ('N', (-1, 0)), ('S', (1, 0)), ('W', (0, -1)), ('E', (0, 1))
#     copied_lines = text.splitlines()
#     grid = [[int(cell in '/\\-|C') for cell in line[2: -2 + (n % 2)]]
#             for n, line in enumerate(copied_lines[2: -2])]
#     first_col = [row[0] for row in grid]
#     for index, x in enumerate(first_col):
#         if x and sum(grid[i][j]  for i in range(max(0, index - 1), index + 2)
#                      for j in (0, 1)) == 2:
#             break
#     path, moves = [(index, 0)], ''
#     while True:
#         r, c = path[-1]
#         for nwse, (dr, dc) in MOVES:
#             pos = x, y = r + 2 * dr, c + 2 * dc
#             if (0 <= x < len(grid) and 0 <= y < len(grid[0])
#                     and grid[r + dr][c + dc] and grid[x][y]
#                     and pos not in path[-2: -1]):
#                 break
#         else:
#             break
#         path.append(pos)
#         moves += nwse
#     pyperclip.copy(moves)
