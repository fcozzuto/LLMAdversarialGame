def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    if res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_self = min(man(nx, ny, rx, ry) for rx, ry in res)
            d_opp = man(ox, oy, res[0][0], res[0][1]) if res else 0
            score = -d_self
            if d_self <= d_opp:
                score += 1
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dist = man(nx, ny, ox, oy)
            score = dist
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]