def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, e):
        return abs(a - c) + abs(b - e)

    # restrict to few promising resources for speed
    res.sort(key=lambda p: md(sx, sy, p[0], p[1]) + 0.25 * md(ox, oy, p[0], p[1]))
    res = res[: min(8, len(res))]

    def move_into_valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not move_into_valid(nx, ny):
            continue

        # choose best resource after this move
        cur_best = None
        cur_tie = None
        for tx, ty in res:
            sd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)
            gap = od - sd
            # prefer positive gaps, then closer target
            val = gap * 100 - sd
            tie = (gap, -sd)
            if cur_best is None or val > cur_best or (val == cur_best and tie > cur_tie):
                cur_best = val
                cur_tie = tie

        # add a mild "front" pressure: advance along our corner direction (x+y)
        front = (nx + ny) - (sx + sy)
        val2 = cur_best + front

        if best_val is None or val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]