def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    rolestr = (observation.get("self_role") or "").lower()
    pursuer = ("evad" not in rolestr)  # default to pursuer

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        try:
            x, y = r[0], r[1]
            res_list.append((x, y))
        except Exception:
            pass

    target = (ox, oy)
    if res_list:
        # choose nearest (for pursuer) or farthest (for evader)
        best = None
        bestv = None
        for rx, ry in res_list:
            d2 = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            v = d2 if not pursuer else -d2
            if best is None or v > bestv:
                best, bestv = (rx, ry), v
        target = best

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d2t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d2o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = (-(d2t) if pursuer else d2t) + (-(d2o) if pursuer else d2o) * 0.05
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]