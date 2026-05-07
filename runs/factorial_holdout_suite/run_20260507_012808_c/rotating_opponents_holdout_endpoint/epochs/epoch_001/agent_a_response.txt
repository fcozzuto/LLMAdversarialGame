def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # pick resource that we can reach sooner than opponent (approx).
    best = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        score = (d_opp - d_self) * 1000 - d_self
        key = (score, -d_self, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, tx, ty)
            moves.append((dist, nx, ny, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], t[2], t[1]))
    return [moves[0][3], moves[0][4]]