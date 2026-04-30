def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestk = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            k = (d, (dx != 0 and dy != 0), abs(nx - tx) + abs(ny - ty))
            if bestk is None or k < bestk:
                bestk, best = k, [dx, dy]
        return best if best is not None else [0, 0]

    # Choose resource target by deterministic competition-aware value.
    best_res = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach relatively earlier; small tie-break to reduce wandering.
        score = (ds - 0.65 * do) * 100 + (ds + do) * 0.01 + (rx + ry) * 0.001
        if best_score is None or score < best_score:
            best_score, best_res = score, (rx, ry)

    rx, ry = best_res
    tx = 0 if rx == sx else (1 if rx > sx else -1)
    ty = 0 if ry == sy else (1 if ry > sy else -1)

    # Primary move toward target; fallback to any move that improves distance.
    preferred = (tx, ty)
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        ds_next = cheb(nx, ny, rx, ry)
        # Encourage the desired direction; penalize non-diagonal when diagonal would be possible.
        dir_bonus = 0 if (dx, dy) == preferred else 0.2
        diag_pref = -0.05 if (tx != 0 and ty != 0 and dx != 0 and dy != 0) else 0
        candidates.append(((ds_next + dir_bonus) + diag_pref, (abs(rx - nx) + abs(ry - ny)), dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]