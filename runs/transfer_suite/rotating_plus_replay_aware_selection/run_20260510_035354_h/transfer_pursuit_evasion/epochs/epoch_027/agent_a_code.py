def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            obs.add((x, y))
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evade = ("evad" in role) or ("purs" not in role and "evad" in opp_role)

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            x, y = int(p[0]), int(p[1])
            res.append((x, y))
        except Exception:
            pass

    best = None
    best_val = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue

            d_op = abs(nx - ox) + abs(ny - oy)
            if res:
                d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
            else:
                d_res = 0

            val = d_res - (d_op if evade else -d_op)
            if best_val is None or (val > best_val) or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]