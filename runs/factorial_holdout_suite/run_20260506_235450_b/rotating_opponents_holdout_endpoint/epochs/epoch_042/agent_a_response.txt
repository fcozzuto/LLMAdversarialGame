def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict):
            if "x" in a and "y" in a:
                x, y = int(a["x"]), int(a["y"])
            else:
                continue
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def parse_xy(v):
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    resources = []
    for r in observation.get("resources") or []:
        p = parse_xy(r)
        if not p:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Prefer resources where we are (materially) closer than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist_cheb(sx, sy, rx, ry)
        opd = dist_cheb(ox, oy, rx, ry)
        # If we can arrive earlier, strongly prefer.
        # Tie-breaker: prefer nearer overall and stable ordering by coord.
        key = (opd - myd, -(myd + opd * 0.05), -rx, -ry)
        if best is None or key > best_key:
            best, best_key = (rx, ry), key

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Choose move that greedily reduces distance to target, with slight preference
    # for moves that increase our lead over the opponent.
    bestm = None
    bestmk = None
    for dx, dy, nx, ny in moves:
        myd2 = dist_cheb(nx, ny, tx, ty)
        opd = dist_cheb(ox, oy, tx, ty)
        lead = opd - myd2
        key = (lead, -(myd2), -(abs(tx - nx) + abs(ty - ny)), -dx, -dy)
        if bestm is None or key > bestmk:
            bestm, bestmk = (dx, dy), key
    return [int(bestm[0]), int(bestm[1])]