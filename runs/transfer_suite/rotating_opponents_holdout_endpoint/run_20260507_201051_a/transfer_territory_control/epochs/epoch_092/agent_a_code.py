def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))
                if len(targets) >= 40:
                    break

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = (10**9, 0, 0)

    def score_to(tx, ty, nx, ny):
        # Prefer getting closer to target; also avoid opponent proximity a bit.
        man = abs(nx - tx) + abs(ny - ty)
        opp = abs(nx - ox) + abs(ny - oy)
        return man - 0.15 * opp

    if not targets:
        # If no unclaimed targets, just move toward opponent territory or away from obstacles.
        targets = [(w - 1, h - 1), (0, 0), (sx, sy)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        smin = 10**9
        for tx, ty in targets:
            s = score_to(tx, ty, nx, ny)
            if s < smin:
                smin = s
        # Small tie-breaker to keep deterministic preference order by (dx,dy) via tuple.
        cand = (smin, dx, dy)
        if cand < best:
            best = cand

    return [int(best[1]), int(best[2])]