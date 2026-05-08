def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in res:
        dself = dist(sx, sy, rx, ry)
        dopp = dist(ox, oy, rx, ry)
        key = (dopp - dself, -dself, -dist(ox, oy, rx, ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dnew = dist(nx, ny, rx, ry)
        dopp = dist(ox, oy, rx, ry)
        # Prefer: minimize distance to target, and be at least as close as opponent.
        eval1 = (dnew - dopp, dnew, dist(ox, oy, nx, ny))
        if best_eval is None or eval1 < best_eval:
            best_eval = eval1
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]