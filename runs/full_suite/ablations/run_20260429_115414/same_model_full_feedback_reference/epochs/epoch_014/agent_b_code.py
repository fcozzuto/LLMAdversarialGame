def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    resources = observation.get("resources") or []
    res = []
    seen = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if (x, y) not in obs and (x, y) not in seen:
                seen.add((x, y))
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    bestd = None
    for (x, y) in res:
        d = man(sx, sy, x, y)
        if target is None or d < bestd or (d == bestd and (x, y) < target):
            target = (x, y)
            bestd = d

    cx, cy = (W - 1) // 2, (H - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if target is not None:
            dres = man(nx, ny, target[0], target[1])
        else:
            dres = man(nx, ny, cx, cy)
        dobj = man(nx, ny, ox, oy)
        v = -dres
        v += 0.2 * dobj  # avoid getting too close to opponent
        v += -0.01 * man(nx, ny, cx, cy)  # slight pull to center if no resources
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]