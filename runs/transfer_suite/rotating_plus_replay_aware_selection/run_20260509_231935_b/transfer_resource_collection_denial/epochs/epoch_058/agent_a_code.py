def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_val = -10**18
    best_resd = None
    best_opd = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        on_resource = (nx, ny) in set(res)
        min_resd = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < min_resd:
                min_resd = d

        min_opd = cheb(nx, ny, ox, oy)

        val = (-min_resd) * 100 + min_opd
        if on_resource:
            val += 10**6

        if (val > best_val) or (val == best_val and (best_resd is None or min_resd < best_resd)) or \
           (val == best_val and min_resd == best_resd and (best_opd is None or min_opd > best_opd)) or \
           (val == best_val and min_resd == best_resd and min_opd == best_opd and (dx > best_move[0] or (dx == best_move[0] and dy > best_move[1]))):
            best_val = val
            best_resd = min_resd
            best_opd = min_opd
            best_move = [dx, dy]

    return best_move