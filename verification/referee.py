"""
CheckiOReferee is a base referee for checking you code.
    arguments:
        tests -- the dict contains tests in the specific structure.
            You can find an example in tests.py.
        cover_code -- is a wrapper for the user function and additional operations before give data
            in the user function. You can use some predefined codes from checkio.referee.cover_codes
        checker -- is replacement for the default checking of an user function result. If given, then
            instead simple "==" will be using the checker function which return tuple with result
            (false or true) and some additional info (some message).
            You can use some predefined codes from checkio.referee.checkers
        add_allowed_modules -- additional module which will be allowed for your task.
        add_close_builtins -- some closed builtin words, as example, if you want, you can close "eval"
        remove_allowed_modules -- close standard library modules, as example "math"
checkio.referee.checkers
    checkers.float_comparison -- Checking function fabric for check result with float numbers.
        Syntax: checkers.float_comparison(digits) -- where "digits" is a quantity of significant
            digits after coma.
checkio.referee.cover_codes
    cover_codes.unwrap_args -- Your "input" from test can be given as a list. if you want unwrap this
        before user function calling, then using this function. For example: if your test's input
        is [2, 2] and you use this cover_code, then user function will be called as checkio(2, 2)
    cover_codes.unwrap_kwargs -- the same as unwrap_kwargs, but unwrap dict.
"""

from checkio import api
from checkio.signals import ON_CONNECT
from checkio.referees.io import CheckiOReferee
# from checkio.referees import cover_codes

from tests import TESTS

from collections import Counter

MOVES = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
OPPOSITE = dict(zip('NSWE', 'SNEW'))


def checker(answer, user_result):
    try:
        # Nearly the same code as initial_code checker.
        rows, columns, start, end, constraints = answer
        start, end, constraints = tuple(start), tuple(end), eval(constraints)
        assert isinstance(user_result, str) and user_result, \
            'You must return a (non-empty) string.'
        forbidden_chars = ''.join(set(user_result) - MOVES.keys())
        assert not forbidden_chars, ('You can only give N, W, S or E as '
                                     f'directions, not: {forbidden_chars}')
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
    except AssertionError as error:
        return False, (error.args[0], None)
    return True, ('Great!', None)
    # Last place was to give data for js visualization, but finally not needed.


# JSON keys can not be tuples. "eval" change big string to the wanted dict.
cover = '''
def cover(func, in_data):
    rows, columns, start, end, constraints = in_data
    return func(rows, columns,
                tuple(start), tuple(end),
                eval(constraints))
'''


api.add_listener(
    ON_CONNECT,
    CheckiOReferee(
        tests=TESTS,
        checker=checker,
        function_name={
            'python': 'train_tracks',
            # 'js': 'trainTracks',
        },
        cover_code={
            'python-3': cover,
            # 'js-node':
        },
    ).on_ready,
)
