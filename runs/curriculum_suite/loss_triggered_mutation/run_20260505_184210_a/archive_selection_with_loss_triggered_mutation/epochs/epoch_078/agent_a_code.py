def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    opp_row_targets = set(r for r in resources if r[1] == oy)

    bestR = None
    bestKey = None
    for r in resources:
        dm = man(me, r)
        do = man(opp, r)
        # prefer resources we reach sooner; tie-break to reduce opponent advantage
        row_bias = -2 if r in opp_row_targets else 0
        key = (0, dm - do + row_bias, dm, r[0], r[1])
        if bestKey is None or key < bestKey:
            bestKey = key
            bestR = r

    tx, ty = bestR

    # one-step lookahead: pick move maximizing expected advantage for current best target,
    # with secondary aim to grab a resource we are likely to win.
    def score_cell(cell):
        dmin = 10**9
        dlead = -10**9
        for r in resources:
            dm = man(cell, r)
            do = man(opp, r)
            if dm < dmin:
                dmin = dm
            dlead = max(dlead, (do - dm) + (-2 if r in opp_row_targets else 0))
        # avoid drifting away from the chosen target
        return (dlead * 10) - man(cell, (tx, ty)) - (0 if cell in resources else 0) - dmin * 0.01

    bestMove = (0, 0)
    bestVal = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        val = score_cell((nx, ny))
        if bestVal is None or val > bestVal or (val == bestVal and (dx, dy) < bestMove):
            bestVal = val
            bestMove = (dx, dy)

    dx, dy = bestMove
    if not (-1 <= dx <= 1 and -1 <= dy <= 1 and isinstance(dx, int) and isinstance(dy, int)):
        return [0, 0]
    return [dx, dy]