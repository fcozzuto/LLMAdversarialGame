def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if not resources:
        cx, cy = w // 2, h // 2
        tx = 0 if cx == sx else (1 if cx > sx else -1)
        ty = 0 if cy == sy else (1 if cy > sy else -1)
        return [tx, ty]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def clamp_step(v, t):
        if t == v: return 0
        return 1 if t > v else -1

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    # Pick target resource with strongest current advantage (deterministic tie-break).
    best_r = resources[0]
    best_key = (-10**18, 10**18, 10**18)
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, sd, rx * 100 + ry)
        if key > best_key:
            best_key = key
            best_r = [rx, ry]
    rx, ry = best_r

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Heuristic: move to reduce distance to target while increasing opponent disadvantage.
        nd = dist(nx, ny, rx, ry)
        sd = dist(sx, sy, rx, ry)
        nod = dist(ox, oy, rx, ry)
        adv_now = nod - nd

        # Obstacle proximity penalty to avoid getting stuck (local only).
        block_pen = 0
        for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            ax, ay = nx + adx, ny + ady
            if (ax, ay) in obstacles:
                block_pen += 0.35

        val = (adv_now * 6.0) + ((sd - nd) * 1.2) - (nd * 0.25) - block_pen

        # Small deterministic preference for progressing (not just staying).
        if dx == 0 and dy == 0:
            val -= 0.08

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]