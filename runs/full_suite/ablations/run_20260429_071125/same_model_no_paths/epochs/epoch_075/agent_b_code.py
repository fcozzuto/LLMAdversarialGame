def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not inb(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**18
    scored_any = False

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        scored_any = True
        if resources:
            # Prefer moves that get closer to the nearest resource.
            d_sr = 10**9
            d_so = dist(nx, ny, ox, oy)
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < d_sr:
                    d_sr = d
            # Small bonus for getting farther from opponent.
            score = -d_sr + 0.05 * d_so
        else:
            # If no resources, try to stay away from opponent.
            score = 0.1 * dist(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if scored_any:
        return best_move
    return [0, 0]