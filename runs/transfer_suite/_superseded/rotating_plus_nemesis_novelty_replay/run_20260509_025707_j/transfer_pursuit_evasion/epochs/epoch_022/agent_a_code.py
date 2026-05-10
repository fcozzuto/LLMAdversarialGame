def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 1 or h < 1 or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    prefer = resources if resources else [(ox, oy)]

    def best_target_for(x, y):
        md = 10**9
        for tx, ty in prefer:
            d = abs(tx - x) + abs(ty - y)
            if d < md:
                md = d
        return md

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_tgt = best_target_for(nx, ny)
        # Score: prioritize nearing nearest resource; if none, approach opponent. Also avoid being too close to opponent.
        score = (-d_tgt * 10) + (-d_opp if resources else (-(d_opp) // 2))
        # tie-break deterministically: prefer smaller dx, then smaller dy, then stay
        tie = (score, -(abs(dx) + abs(dy)), -dx, -dy)
        if best is None or tie > best_score:
            best_score = tie
            best = (dx, dy)

    return [0, 0] if best is None else [int(best[0]), int(best[1])]