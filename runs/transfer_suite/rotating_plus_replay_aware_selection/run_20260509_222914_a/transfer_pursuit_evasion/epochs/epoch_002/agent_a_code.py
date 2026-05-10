def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursur" in self_role) or ("pursuit" in self_role)
    if "evad" in self_role:
        pursuer = False
    if "evad" in opponent_role and pursuer and "evad" not in self_role:
        # unlikely, but keep consistent: if opponent is evading and we are pursuer, still pursuer=True
        pass

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Tie-breaker: prefer moves that are lexicographically earlier for determinism.
    best_score = None
    best_move = (0, 0)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # If pursuer: minimize distance; if evader: maximize distance.
        score = d2 if not pursuer else -d2
        # Small center bias to break ties deterministically (closer to center slightly preferred).
        cb = -(abs(nx - cx) + abs(ny - cy)) * 1e-6
        score += cb
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]