def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    # Heuristic: if we are the evader, maximize distance; if pursuer, minimize.
    we_evade = ("evader" in self_role) or ("evade" in self_role) or ("evader" not in opp_role and "pursuer" in opp_role) or ("evader" in opp_role and "pursuer" in self_role is False)

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obs:
                continue
            d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # Center bias to reduce easy trapping; deterministic tie-break by dx,dy order.
            center_bias = (nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2
            if we_evade:
                primary = (-d2, center_bias)
            else:
                primary = (d2, center_bias)
            cand = (primary, dx, dy)
            if best is None or cand < best:
                best = cand

    if best is None:
        return [0, 0]
    return [best[1], best[2]]