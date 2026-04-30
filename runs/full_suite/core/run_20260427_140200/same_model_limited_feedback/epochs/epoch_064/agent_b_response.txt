def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs_set = set((p[0], p[1]) for p in obstacles)
    in_bounds = lambda x, y: 0 <= x < w and 0 <= y < h

    if resources:
        best = None
        for rx, ry in resources:
            myd = abs(rx - sx) + abs(ry - sy)
            opd = abs(rx - ox) + abs(oy - rx)  # small asymmetry to break ties
            key = (myd - 0.35 * opd, myd)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources known: head toward opponent slightly to prevent easy capture
        tx, ty = ox, oy

    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            # Prefer moving closer to target and (secondarily) away from opponent
            myd = abs(tx - nx) + abs(ty - ny)
            opd = abs(ox - nx) + abs(oy - ny)
            # Small tie-breaker favors diagonal when it doesn't conflict
            diag_bonus = 0.02 if dx != 0 and dy != 0 else 0.0
            candidates.append(((myd - 0.2 * opd) - diag_bonus, myd, -opd, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][3]), int(candidates[0][4])]