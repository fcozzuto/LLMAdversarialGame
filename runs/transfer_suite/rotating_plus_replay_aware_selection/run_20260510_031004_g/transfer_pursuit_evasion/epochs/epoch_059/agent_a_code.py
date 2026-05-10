def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = True
    if "evad" in self_role:
        is_pursuer = False
    elif "evad" in opponent_role:
        is_pursuer = True

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    # Greedy: minimize distance if pursuer, maximize if evader. Deterministic tie-breaks.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_dxdy = (0, 0)
    # small center bias to break ties: pursuer toward center, evader away
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d1 = abs(nx - ox) + abs(ny - oy)
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        center_dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        # score: for pursuer lower distance is better; for evader higher is better
        if is_pursuer:
            val = (d1, d2, -center_dist)
        else:
            val = (-d1, -d2, center_dist)
        if best is None or val < best or (val == best and (dx, dy) < best_dxdy):
            best = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]