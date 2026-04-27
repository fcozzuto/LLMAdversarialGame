def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (10**18, (0, 0))

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dmin = 10**18
            for rx, ry in resources:
                dd = dist(nx, ny, rx, ry)
                if dd < dmin:
                    dmin = dd
            score = dmin * 10 + dist(nx, ny, ox, oy)  # also prefer not moving onto opponent vicinity
            if score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
    else:
        tx, ty = (w - 1, h - 1) if (ox + oy) <= (w - 1 + h - 1) / 2 else (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = dist(nx, ny, tx, ty) - dist(nx, ny, ox, oy)  # approach corner, keep away from opponent
            if score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))

    dx, dy = best[1]
    if not valid(sx + dx, sy + dy):
        return [0, 0]
    return [int(dx), int(dy)]