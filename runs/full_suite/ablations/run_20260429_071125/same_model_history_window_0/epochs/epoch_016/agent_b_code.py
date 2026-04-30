def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer than opponent; tie-break by closer total distance, then position.
        key = (-(myd - opd), myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        # Also penalize moving closer to opponent if we can't reach resources advantageously.
        opp_dist = cheb(nx, ny, ox, oy)
        candidates.append(((dist, -opp_dist), dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0][0], -t[0][1], t[1], t[2]))
    return [candidates[0][1], candidates[0][2]]