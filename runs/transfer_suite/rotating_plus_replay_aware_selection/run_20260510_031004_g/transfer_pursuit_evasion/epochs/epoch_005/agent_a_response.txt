def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    we_evade = ("evader" in self_role) or ("evade" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)

    dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            dirs.append((dx, dy))

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if we_evade:
            # Increase distance; keep away from edges to avoid corner trap.
            edge_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
            center_bias = edge_dist
            key = (d2, center_bias, -dx, -dy)  # deterministic tie-break
            better = best_key is None or key > best_key
        else:
            # Pursue: decrease distance; also avoid edges if tied.
            edge_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
            key = (-d2, edge_dist, dx, dy)  # deterministic tie-break
            better = best_key is None or key > best_key

        if better:
            best_key = key
            best = [dx, dy]

    if best is None:
        # Fallback: stay put (engine will keep us in place if invalid)
        return [0, 0]
    return best