def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                res.append((x, y))

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if res:
            # Prefer moves that reduce distance to resources relative to opponent.
            r = min(dist2(nx, ny, rx, ry) for rx, ry in res)
            o = min(dist2(ox, oy, rx, ry) for rx, ry in res)
            score = (r - o, dist2(nx, ny, ox, oy))
        else:
            # No resources: move away from opponent.
            score = (-dist2(nx, ny, ox, oy), abs(nx - ox) + abs(ny - oy))
        # Deterministic tie-break: lexicographic on move.
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]