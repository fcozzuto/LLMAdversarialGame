def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not resources or not legal:
        return [0, 0]

    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach strictly earlier; otherwise minimize opponent lead and own distance.
        key = (0, ds, do) if ds < do else (1, (do - ds), ds, do)
        if best is None or key < best[0]:
            best = (key, rx, ry, ds, do)
    _, tx, ty, _, _ = best

    # Deterministic greedy step towards target with tie-break favoring keeping distance to opponent larger.
    opp_best = None
    chosen = (0, 0, sx, sy)
    for dx, dy, nx, ny in legal:
        dist_to_target = cheb(nx, ny, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)
        key = (dist_to_target, -opp_dist, dx, dy)
        if opp_best is None or key < opp_best:
            opp_best = key
            chosen = (dx, dy, nx, ny)

    return [chosen[0], chosen[1]]