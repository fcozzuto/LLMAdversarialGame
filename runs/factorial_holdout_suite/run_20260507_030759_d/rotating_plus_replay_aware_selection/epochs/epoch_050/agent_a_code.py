def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target resource where we are not behind opponent (prefer closest such),
    # otherwise fall back to overall closest.
    best_res = None
    best_key = None
    any_tied = False
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        if d_me <= d_op:
            any_tied = True
            key = (d_me, d_op, abs(rx - ox) + abs(ry - oy))
        else:
            key = (10**6 + d_me, d_op, abs(rx - ox) + abs(ry - oy))
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    if not best_res and resources:
        best_res = resources[0]
    rx, ry = best_res

    # Score each move by: can collect immediately, then resulting distance to target,
    # then advantage vs opponent, then obstacle safety (already ensured), and slight
    # bias toward central progress.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        collect = 1 if (nx, ny) == (rx, ry) else 0
        d_me = man(nx, ny, rx, ry)
        d_op = man(ox, oy, rx, ry)
        adv = d_op - d_me  # positive is good
        center_bias = - (abs(nx - cx) + abs(ny - cy)) * 0.001
        score_tuple = (collect, adv, -d_me, center_bias)
        if best_score is None or score_tuple > best_score:
            best_score = score_tuple
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]