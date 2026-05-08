def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("direct" in role and "evad" not in role) or (role == "")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            return -10**9 if is_pursuer else -10**9
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy

        # wall/obstacle proximity shaping
        wall = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
        wall_pen = -wall

        # prefer staying out of "dead-end" obstacle adjacency
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inside(tx, ty) and (tx, ty) in oset:
                    adj_obs += 1

        # deterministic: small tie-break by move order handled later
        if is_pursuer:
            return (-dist2 * 10) + (wall_pen * 0.5) - adj_obs
        else:
            return (dist2 * 10) + (wall_pen * -0.5) - adj_obs

    best = None
    bestv = None
    for i, (dx, dy) in enumerate(moves):
        v = score_move(dx, dy)
        if bestv is None or v > bestv or (v == bestv and i < best[0]):
            bestv = v
            best = (i, dx, dy)

    return [best[1], best[2]]