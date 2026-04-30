def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    res = observation.get("resources", [])
    obs_set = set((x, y) for x, y in obstacles)
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not res:
        # Fallback: drift toward center while avoiding obstacles
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None; bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obs_set: 
                continue
            v = (abs(nx - cx) + abs(ny - cy))
            if bestv is None or v < bestv:
                bestv = v; best = (dx, dy)
        return list(best if best is not None else (0, 0))
    # Choose a target resource with a bias away from opponent
    best_t = None; best_score = None
    for (rx, ry) in res:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Prefer resources closer to us; break ties by being farther from opponent
        sc = ds - 0.2 * do
        if best_score is None or sc < best_score:
            best_score = sc; best_t = (rx, ry)
    rx, ry = best_t
    # Evaluate immediate moves by distance to target, with safety/anti-blocking
    best = (0, 0); bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obs_set: 
            continue
        ds_new = abs(rx - nx) + abs(ry - ny)
        # Mildly discourage moving adjacent to opponent to reduce swapping races
        adj_opp = 1 if abs(nx - ox) <= 1 and abs(ny - oy) <= 1 else 0
        # Prefer stepping onto resource if available
        on_res = 1 if (nx, ny) in set((x, y) for x, y in res) else 0
        v = (ds_new, adj_opp, -on_res)
        if bestv is None or v < bestv:
            bestv = v; best = (dx, dy)
    return [int(best[0]), int(best[1])]