def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)

    env = observation.get("environment_name", "")
    role = observation.get("self_role", "")
    if env != "pursuit_evasion":
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    if role == "evader":
        # Deterministic evasion: run to farthest corner from pursuer.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        # Pursuer: target opponent directly, but choose best legal step.
        tx, ty = ox, oy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d_before = max(abs(sx - ox), abs(sy - oy))
        d_after = max(abs(nx - ox), abs(ny - oy))
        # Prefer biggest distance reduction; if close, prefer moving away from evader prediction (corner bias).
        dist_to_target = abs(nx - tx) + abs(ny - ty)
        # Small deterministic tie-break: lexicographic by dx,dy via computed tuple order.
        score = (d_before - d_after, -dist_to_target, -abs(nx - (w - 1)) - abs(ny - (h - 1)), -dx, -dy)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]