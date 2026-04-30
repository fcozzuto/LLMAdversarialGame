def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_best = min(cheb(ox, oy, rx, ry) for rx, ry in res)

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        my_best = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        # Prefer reducing own distance, while maintaining/creasing relative advantage over opponent.
        val = (opp_best - my_best) * 1000 - my_best
        # Subtle tie-break: prefer staying closer to grid center to keep options open.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val -= (abs(nx - cx) + abs(ny - cy)) * 0.01
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move == [0, 0] and (sx, sy) in obs:
        return [0, 0]
    return best_move