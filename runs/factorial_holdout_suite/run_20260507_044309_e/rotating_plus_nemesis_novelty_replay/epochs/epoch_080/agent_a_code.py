def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)

    resources = observation.get("resources") or []
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            val = cheb(nx, ny, ox, oy)
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    target = resources[0]
    bestd = cheb(sx, sy, target[0], target[1])
    for r in resources[1:]:
        d = cheb(sx, sy, r[0], r[1])
        if d < bestd or (d == bestd and (r[0], r[1]) < (target[0], target[1])):
            bestd = d
            target = r

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_res = cheb(nx, ny, target[0], target[1])
        d_opp = cheb(nx, ny, ox, oy)
        val = (-d_res) * 1000 + d_opp
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]