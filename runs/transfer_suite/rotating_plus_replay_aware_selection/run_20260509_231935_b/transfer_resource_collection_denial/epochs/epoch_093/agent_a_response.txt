def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_raw if p and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obstacle(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        best = valid[0]
        bestv = -10**18
        for dx, dy, nx, ny in valid:
            v = -(cheb(nx, ny, ox, oy)) - 0.2 * near_obstacle(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy, nx, ny)
        return [best[0], best[1]]

    # Target selection: prefer resources we can reach strictly earlier; otherwise closest.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ts = cheb(sx, sy, rx, ry)
        to = cheb(ox, oy, rx, ry)
        ahead = ts - to  # negative means we arrive first
        key = (ahead, ts, cheb(sx, sy, rx, ry) + near_obstacle(rx, ry) * 0.1)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)
    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Choose move that maximizes (being closer sooner than opponent) and avoids obstacles.
    best = valid[0]
    bestv = -10**18
    for dx, dy, nx, ny in valid:
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Encourage reducing distance to target and increasing our advantage.
        v = (-ns) + 0.7 * (no - ns) - 0.2 * near_obstacle(nx, ny)
        # Small deterministic bias to break ties: toward target direction.
        v += 1e-6 * (dx * (1 if tx > nx else -1 if tx < nx else 0) + dy * (1 if ty > ny else -1 if ty < ny else 0))
        if v > bestv:
            bestv = v
            best = (dx, dy, nx, ny)
    return [best[0], best[1]]