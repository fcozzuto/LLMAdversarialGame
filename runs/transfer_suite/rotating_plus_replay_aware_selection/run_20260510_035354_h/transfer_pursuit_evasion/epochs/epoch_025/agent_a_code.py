def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)
    role = (observation.get("self_role") or "").lower()
    i_pursuer = ("purs" in role) or ("evad" not in role and (observation.get("opponent_role") or "").lower().find("evad") != -1)
    dxs = (-1, 0, 1); dys = (-1, 0, 1)
    best = None
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            score = d if i_pursuer else -d
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
    return best[1] if best is not None else [0, 0]