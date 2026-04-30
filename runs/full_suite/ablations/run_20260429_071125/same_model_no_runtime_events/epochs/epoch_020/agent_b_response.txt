def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and isinstance(r.get("pos"), (list, tuple)) and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            else:
                x = r.get("x", None)
                y = r.get("y", None)
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources or not valid(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if valid(nx, ny):
                    return [dx, dy]
        return [0, 0]

    candidates = [(sx + dx, sy + dy, dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if valid(sx + dx, sy + dy)]
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach much earlier than opponent; slight focus on closeness to progress.
        key = (myd - opd * 0.35, myd, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    best_move = (0, 0, None)
    for nx, ny, dx, dy in candidates:
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cheb(ox, oy, rx, ry)
        # After moving, prefer reduced distance; also avoid giving opponent a faster claim by staying nearer to target.
        # Deterministic tie-break by coordinates.
        score = (myd2, (myd2 - (opd2 * 0.35)), nx, ny)
        if best_move[2] is None or score < best_move[2]:
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]