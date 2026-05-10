def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((p[0], p[1]))

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Target selection: race resources we can likely secure first; tie-break deterministically.
    best_key = None
    target = None
    for rx, ry in resources:
        if not in_bounds(rx, ry):
            continue
        myd = dist_cheb(sx, sy, rx, ry)
        opd = dist_cheb(ox, oy, rx, ry)
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        # Prefer myd much smaller than opd; otherwise closer and deterministic.
        val = (myd - 0.75 * opd) + 0.01 * myd + 0.001 * center_bias
        key = (val, myd, -opd, rx + ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    tx, ty = target
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                pass
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obs_set:
                continue
            step_score = 0
            # Move preference toward target and away from edges; deterministically weight.
            step_score += dist_cheb(nx, ny, tx, ty) * 10
            step_score += abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
            # Slight preference for aligning with direct delta to target.
            step_score += (0 if dx == dx0 else 1) + (0 if dy == dy0 else 1) * 0.01
            # If opponent is closer to target, avoid wasting steps: encourage progress.
            step_score += max(0, dist_cheb(nx, ny, tx, ty) - dist_cheb(sx, sy, tx, ty)) * 0.05
            candidates.append((step_score, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    return [candidates[0][3], candidates[0][4]]