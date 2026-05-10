def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
        best = [0, 0]
        bd = man(sx, sy, ox, oy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = man(nx, ny, ox, oy)
                if d < bd:
                    bd, best = d, [dx, dy]
        return best

    target = min(res, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = man(nx, ny, target[0], target[1])
        val = -d
        d2 = man(nx, ny, ox, oy)
        val += -0.05 * d2
        if val > best_val:
            best_val, best_move = val, [dx, dy]

    nx, ny = sx, sy
    if best_move == [0, 0] and (nx, ny) in obs:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            tx, ty = sx + dx, sy + dy
            if inb(tx, ty) and (tx, ty) not in obs:
                return [dx, dy]
    return best_move