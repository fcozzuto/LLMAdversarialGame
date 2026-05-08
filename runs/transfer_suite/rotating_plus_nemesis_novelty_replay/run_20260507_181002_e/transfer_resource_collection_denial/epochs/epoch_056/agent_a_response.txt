def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = pos(observation.get("self_position", None), (0, 0))
    ox, oy = pos(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is None:
            continue
        x, y = pos(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r is None:
            continue
        x, y = pos(r, None)
        if x is None:
            continue
        if free(x, y):
            resources.append((x, y))

    if not resources:
        tx, ty = (w - 1, h - 1) if (sx, sy) != (0, 0) else (0, 0)
        best_dx = 0
        best_dy = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not free(nx, ny):
                    continue
                d = abs(tx - nx) + abs(ty - ny)
                if d < abs(tx - sx) + abs(ty - sy):
                    return [dx, dy]
        return [0, 0]

    # Choose among 9 candidate moves by best guaranteed advantage at next position.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        moves = [(0, 0, sx, sy)]

    best = None
    for dx, dy, nx, ny in moves:
        # Score resources: maximize (opp_dist - self_dist_next), then prefer smaller self_dist_next.
        best_key = None
        for tx, ty in resources:
            self_d = abs(tx - nx) + abs(ty - ny)
            opp_d = abs(tx - ox) + abs(ty - oy)
            key = (opp_d - self_d, -self_d, -abs(tx - nx), -abs(ty - ny))
            if best_key is None or key > best_key:
                best_key = key
        key2 = best_key
        if best is None or key2 > best[0]:
            best = (key2, dx, dy)

    return [int(best[1]), int(best[2])]