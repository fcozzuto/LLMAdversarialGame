def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles:
        return [0, 0]
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Tie-break deterministically by move priority.
    # Prefer moves with larger (toward resource) then farther from opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in res_set:
            score = 10_000 - man(nx, ny, ox, oy)
        else:
            dmin = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
            dop = man(nx, ny, ox, oy)
            # Encourage approach to nearest resource, but keep some distance from opponent.
            score = (-100 * dmin) + (5 * dop)

            # If opponent is close, add slight penalty for moving closer to opponent.
            if man(sx, sy, ox, oy) <= 2:
                score -= (10 * (man(nx, ny, ox, oy) < man(sx, sy, ox, oy)))

        pri = (dx + 1, dy + 1)  # deterministic small preference
        key = (score, -pri[0], -pri[1])
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]