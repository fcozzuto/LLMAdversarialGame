def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource to race for: maximize (opp_dist - my_dist), tie-break by my_dist.
    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        win = oppd - myd
        # Prefer closer resources when race advantage is similar; also prefer central.
        center = cheb(rx, ry, w // 2, h // 2)
        key = (win, -myd, -center, -(rx * 9 + ry))
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    # Choose next step: among legal moves, maximize improvement in race distance; avoid obstacles.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            myd_now = cheb(sx, sy, tx, ty)
            myd_next = cheb(nx, ny, tx, ty)
            oppd = cheb(ox, oy, tx, ty)
            # Bigger is better: race gain + progress.
            val = (oppd - myd_next) * 100 - myd_next
            # Discourage stepping away in both axes too much.
            val -= 0.1 * ((tx - nx) ** 2 + (ty - ny) ** 2) ** 0.5
            # Slightly prefer diagonals only if they reduce distance.
            if dx != 0 and dy != 0 and myd_next >= myd_now:
                val -= 0.5
            candidates.append((val, dx, dy))
    candidates.sort(reverse=True)
    return [candidates[0][1], candidates[0][2]]