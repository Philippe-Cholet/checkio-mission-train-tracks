# Replace this function by yours!
def train_tracks(rows, columns, start, end, constraints):
    return 'NNNESESEENENESSSESSWWSWWSEEE'


# Then test all the "GAME_IDS" you want from the url page or "tracks.exe".
if __name__ == '__main__':
    import re
    import itertools as it
    from copy import deepcopy
    from collections import Counter

    GAME_IDS = [
        '10x10:p3kAa9zc6qArCb,6,3,2,2,5,3,5,S5,9,5,7,9,5,5,3,2,S2,4,4,4',
    ]

    def define_input(game_id):
        TABLE = {'3': 'NE', '5': 'WE', '6': 'NW',
                 '9': 'SE', 'A': 'NS', 'C': 'SW'}
        match = re.fullmatch(r'(\d+)x(\d+):([^,]+),([S0-9,]+)', game_id)
        assert match
        ncols, nrows, line, S_counts = match.groups()
        ncols, nrows = int(ncols), int(nrows)
        S_counts = S_counts.split(',')
        columns, rows = S_counts[:ncols], S_counts[ncols:]
        xA, yB = (next(i for i, item in enumerate(lst) if 'S' in item)
                  for lst in (rows, columns))
        yA, xB = 0, nrows - 1
        start, end = (xA, yA), (xB, yB)
        columns = [int(s.replace('S', '')) for s in columns]
        rows = [int(s.replace('S', '')) for s in rows]
        line = it.chain.from_iterable([TABLE[s]] if s in TABLE else
                                      [''] * (ord(s) - ord('a') + 1)
                                      for s in line)
        grid = [[next(line) for _ in range(ncols)] for _ in range(nrows)]
        grid[xA][yA] = grid[xA][yA].replace('W', '')
        grid[xB][yB] = grid[xB][yB].replace('S', '')

        constraints = {(i, j): set(dirs) for i, row in enumerate(grid)
                       for j, dirs in enumerate(row) if dirs}
        return rows, columns, start, end, constraints

    def checker(test, user_result):
        assert isinstance(user_result, str) and user_result, \
            'You must return a (non-empty) string.'
        MOVES = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
        forbidden_chars = ''.join(set(user_result) - MOVES.keys())
        assert not forbidden_chars, ('You can only give N, W, S or E as '
                                     f'directions, not: {forbidden_chars}')
        OPPOSITE = dict(zip('NSWE', 'SNEW'))
        rows, columns, start, end, constraints = test
        path = [start]
        for step, nwse in enumerate(user_result, 1):
            r, c = last = path[-1]
            if last in constraints:
                assert nwse in constraints[last], \
                    f'You can not get out of {last} with {nwse!r}.'
                constraints[last].remove(nwse)
            dr, dc = MOVES[nwse]
            position = r, c = r + dr, c + dc
            assert 0 <= r < len(rows) and 0 <= c < len(columns), \
                f'You are outside the grid at {position} after {step} moves.'
            assert position not in path, \
                f'You can not pass twice at {position}.'
            if position in constraints:
                assert OPPOSITE[nwse] in constraints[position], \
                    f'You can not enter at {position} with {nwse!r}.'
                constraints[position].remove(OPPOSITE[nwse])
            path.append(position)
            if position == end:
                assert len(user_result) == step, \
                    (f'You reached the end after {step} moves, '
                     'why are you continuing?')
                break
        else:
            raise AssertionError(f'After all your {step} moves, '
                                 'you still have not reached the end!')
        constraints = {k: v for k, v in constraints.items() if v}
        assert not constraints, (f'{sum(map(len, constraints.values()))}'
                                 ' constraints not respected.')
        all_res_counts = (('Row',    rows,    Counter(i for i, _ in path)),
                          ('Column', columns, Counter(j for _, j in path)))
        for row_or_col, lines, res_counts in all_res_counts:
            for i, count in enumerate(lines):
                assert res_counts[i] == count, \
                    (f'{row_or_col} {i}: you passed by {res_counts[i]} cells '
                     f'instead of {count}.')

    for game_id in GAME_IDS:
        test = define_input(game_id)
        user_result = train_tracks(*deepcopy(test))
        try:
            checker(test, user_result)
            print(f'You solved "{game_id}"')
        except AssertionError as error:
            print(f'You failed "{game_id}":', *error.args)
