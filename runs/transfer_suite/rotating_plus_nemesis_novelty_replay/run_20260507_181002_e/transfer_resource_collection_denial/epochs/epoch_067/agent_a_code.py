def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = get_xy(observation.get("self_position", None), (0, 0))
    ox, oy = get_xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = get_xy(r, None)
        if x is None:
            continue
        if free(x, y):
            resources.append((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = (ox, oy)
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            val = -(abs(tx - nx) + abs(ty - ny))
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Prefer moves that make us closer than opponent to some resource; otherwise maximize advantage.
        cur_best = -10**18
        for tx, ty in resources:
            self_d = abs(tx - nx) + abs(ty - ny)
            opp_d = abs(tx - ox) + abs(ty - oy)
            # Strongly prefer resources where we are not behind; tie-break toward closer self_d.
            advantage = opp_d - self_d
            behind_pen = 0 if advantage >= 0 else -1000 - self_d
            val = advantage * 10 - self_d + behind_pen
            if val > cur_best:
                cur_best = val
        # Small tie-break to reduce distance to currently best resource.
        if cur_best > best_val:
            best_val = cur_best
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]