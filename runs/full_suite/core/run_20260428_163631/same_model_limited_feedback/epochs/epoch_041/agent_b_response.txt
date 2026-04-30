def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in resources:
            d_self = abs(rx - sx) + abs(ry - sy)
            d_opp = abs(rx - ox) + abs(ry - oy)
            # Prefer targets we are closer to; break ties by distance then coordinates.
            key = (d_opp - d_self, d_self, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    # Evaluate candidate moves.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_mv = (None, None)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist_to_target = abs(tx - nx) + abs(ty - ny)
        # Discourage giving opponent an immediate advantage by moving adjacent/closer to same target.
        dist_opp_after = abs(tx - ox) + abs(ty - oy)
        opp_same = 1 if dist_opp_after <= abs(tx - sx) + abs(ty - sy) else 0
        opp_prox = abs(ox - nx) + abs(oy - ny)
        # Strongly prefer capturing/resources-adjacent; otherwise greedy toward target.
        res_here = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0
        val = (0
               - 1000 * res_here
               + dist_to_target
               + (50 * opp_same)
               - (0.8 * opp_prox))
        # Deterministic tie-break: smaller dx, then dy, then lexicographic position via val.
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_mv[0]):
            best_val = val
            best_mv = ((dx, dy), (nx, ny))
    if best_mv[0] is not None:
        dx, dy = best_mv[0]
        return [dx, dy]
    return [0, 0]