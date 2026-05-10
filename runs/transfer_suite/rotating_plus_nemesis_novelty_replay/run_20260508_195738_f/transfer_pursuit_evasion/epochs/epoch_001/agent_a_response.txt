def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chase" in self_role)
    # If roles unclear, infer: pursuer likely has "pursuer" in name.
    if ("purs" not in self_role) and ("evad" not in self_role) and ("purs" in opponent_role):
        is_pursuer = False

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]
    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        dxo, dyo = ox - nx, oy - ny
        dist2 = dxo * dxo + dyo * dyo
        # Pursuer: minimize distance; Evader: maximize distance.
        val = -dist2 if is_pursuer else dist2
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]