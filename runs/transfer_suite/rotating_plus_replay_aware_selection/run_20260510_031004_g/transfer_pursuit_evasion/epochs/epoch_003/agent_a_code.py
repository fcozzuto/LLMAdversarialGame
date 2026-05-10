def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
                candidates.append((d2, dx, dy))
    if not candidates:
        return [0, 0]

    best = min(candidates, key=lambda t: (t[0], t[1], t[2]))
    return [best[1], best[2]]