def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources or ox is None or oy is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
                best = (sc, dx, dy)
        return [best[1], best[2]]
    # Intercept/advantage: pick the move that maximizes (opp_dist - self_dist) to the best reachable resource.
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_adv_for_move = -10**18
        best_tiebreak = (10**9, 10**9)
        for rx, ry in resources:
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            adv = opp_d - self_d
            # Prefer higher advantage; if tied, prefer smaller self_d then smaller coords for determinism.
            if adv > best_adv_for_move or (adv == best_adv_for_move and (self_d < best_tiebreak[0] or (self_d == best_tiebreak[0] and (rx, ry) < best_tiebreak[1]))):
                best_adv_for_move = adv
                best_tiebreak = (self_d, (rx, ry))
        # Add slight pressure to keep moving toward a currently-best resource.
        sc = best_adv_for_move * 100 - best_tiebreak[0]
        if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)
    return [best[1], best[2]]