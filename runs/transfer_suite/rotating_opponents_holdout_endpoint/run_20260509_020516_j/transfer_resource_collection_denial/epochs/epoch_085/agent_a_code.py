def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Score resources by distance advantage and a small bias to smaller self distance.
    best = None
    best_adv = -10**9
    best_sd = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer (better)
        if adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv, best_sd, best = adv, sd, (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # If target step hits an obstacle, try alternative deterministic greedy neighbor.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        moves = [(dx, 0), (0, dy), (dx, dy), (0, 0)]
        # Deterministic order: diagonal, then horizontal, then vertical, then stay? We'll use fixed priority below.
        moves = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        for mx, my in moves:
            tx, ty = sx + mx, sy + my
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                return [mx, my]
        return [0, 0]

    return [dx, dy]