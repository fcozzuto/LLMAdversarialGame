def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    cand = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                cand.append((x, y))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not cand:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = sx + dx, sy + dy
                    if free(nx, ny):
                        return [dx, dy]
        return [0, 0]

    # Choose a target resource by "denial": prefer cells we can reach sooner than opponent.
    best = None
    for x, y in cand:
        myd = md(sx, sy, x, y)
        opd = md(ox, oy, x, y)
        adv = opd - myd  # higher is better
        # tie-break: smaller myd, then deterministic by coordinates
        key = (adv, -myd, -x, -y)
        if best is None or key > best[0]:
            best = (key, x, y)
    _, tx, ty = best

    # Local one-step lookahead: among legal moves, pick one maximizing improved denial and progress.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, None)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd2 = md(nx, ny, tx, ty)
        # Denial from the next position (opponent assumed stationary for 1-step eval)
        opd = md(ox, oy, tx, ty)
        adv2 = opd - myd2
        # Also lightly encourage moving toward target direction.
        dir_bonus = 0
        if (tx - sx) == 0 and (ty - sy) == 0:
            dir_bonus = 0
        else:
            dir_bonus = 1 if (dx == (1 if tx > sx else -1 if tx < sx else 0) or dx == 0) and (dy == (1 if ty > sy else -1 if ty < sy else 0) or dy == 0) else 0
        key = (adv2, -myd2, dir_bonus, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]