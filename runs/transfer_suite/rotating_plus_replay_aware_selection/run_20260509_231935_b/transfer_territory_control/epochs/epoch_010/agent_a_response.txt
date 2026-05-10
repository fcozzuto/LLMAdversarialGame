def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obs_set = {tuple(p) for p in (observation.get("obstacles") or [])}
    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}

    cx, cy = w / 2.0, h / 2.0
    if opp_set:
        sx2 = 0.0
        sy2 = 0.0
        n = len(opp_set)
        for x, y in opp_set:
            sx2 += x
            sy2 += y
        cx, cy = sx2 / n, sy2 / n

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**30

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
            continue

        val = 0.0
        if (nx, ny) in opp_set:
            val += 40.0
        if (nx, ny) in un_set:
            dist_c = abs(nx - cx) + abs(ny - cy)
            center_bias = (w - 1) / 2.0
            val += 10.0 + 1.2 * dist_c / (center_bias + 1e-9)

        # Encourage expansion, discourage giving opponent immediate contact
        adj_own = 0
        adj_opp = 0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in self_set:
                adj_own += 1
            if (tx, ty) in opp_set:
                adj_opp += 1
        val += 2.0 * adj_own
        val -= 3.0 * adj_opp

        # Deterministic tie-break: prefer staying/low dx, then low dy
        key = (0 if (dx, dy) == (0, 0) else 1, abs(dx), abs(dy), dx, dy)
        if val > best_val or (val == best_val and (best is None or key < best[0])):
            best_val = val
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]