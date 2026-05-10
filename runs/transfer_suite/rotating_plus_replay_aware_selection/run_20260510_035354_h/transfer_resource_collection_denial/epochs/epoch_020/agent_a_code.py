def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Choose a target where we have relative advantage (opponent_dist - my_dist),
    # then prefer nearer targets to finish first.
    best = None
    tx = ty = resources[0]
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        cand = (opd - myd, -myd, -rx, -ry)
        if best is None or cand > best:
            best = cand
            tx, ty = rx, ry

    # Obstacle-aware local step: pick neighbor (incl. stay) minimizing distance to target.
    best_step = None
    best_d = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            cand = (d, abs(dx), abs(dy), dx, dy)  # deterministic tie-break
            if best_step is None or cand < best_d:
                best_d = cand
                best_step = [dx, dy]

    if best_step is None:
        return [0, 0]
    return best_step