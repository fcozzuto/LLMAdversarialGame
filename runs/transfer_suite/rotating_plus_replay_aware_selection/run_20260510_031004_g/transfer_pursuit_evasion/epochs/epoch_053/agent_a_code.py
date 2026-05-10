def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    if "evad" in self_role:
        is_pursuer = False
    elif "evad" in opponent_role:
        is_pursuer = True
    else:
        is_pursuer = True

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_pursuer:
        tx, ty = ox, oy
    else:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_opp = max(abs(nx - ox), abs(ny - oy))  # capture radius 0: use fast-to-touch metric
        d_tx = abs(nx - tx) + abs(ny - ty)

        if is_pursuer:
            score = (-d_opp) * 10 - d_tx  # chase opponent; also keep moving toward its position
        else:
            # flee from pursuer, but avoid obstacles and tight walls
            nearest_obs = 0
            if obs:
                nearest_obs = min(abs(nx - ax) + abs(ny - ay) for (ax, ay) in obs)
            wall_dist = min(nx, ny, w - 1 - nx, h - 1 - ny)
            score = (d_opp) * 10 + nearest_obs - d_tx - (1.0 / (1 + wall_dist))

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]