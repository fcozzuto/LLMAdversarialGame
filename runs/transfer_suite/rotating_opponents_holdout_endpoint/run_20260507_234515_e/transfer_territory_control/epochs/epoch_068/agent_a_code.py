def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    targets = []
    res = observation.get("resources") or []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        uc = observation.get("unclaimed_cells") or []
        for p in uc:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obstacles:
                    targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_to_t = 0
        if targets:
            d_to_t = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        # Prefer capturing/approaching targets; otherwise head to opponent; deterministic tie-break.
        score = (0 if targets else 1, d_to_t if targets else 0, d_to_opp)
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]