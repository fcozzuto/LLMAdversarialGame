def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    self_pos = observation.get("self_position", [0, 0]) or [0, 0]
    opponent_pos = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = self_pos[0], self_pos[1]
    oxp, oyp = opponent_pos[0], opponent_pos[1]

    obs = set((int(p[0]), int(p[1])) for p in obstacles if p is not None and len(p) >= 2)

    def clamp(nx, ny):
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= w: nx = w - 1
        if ny >= h: ny = h - 1
        return nx, ny

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best = None
    best_adv = -10**9
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        myd = dist(sx, sy, rx, ry)
        opd = dist(oxp, oyp, rx, ry)
        adv = opd - myd
        if adv > best_adv:
            best_adv = adv
            best = (rx, ry)
    tx, ty = best

    best_move = (0, 0)
    best_score = 10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obs:
                nx, ny = sx, sy
            score = dist(nx, ny, tx, ty)
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]