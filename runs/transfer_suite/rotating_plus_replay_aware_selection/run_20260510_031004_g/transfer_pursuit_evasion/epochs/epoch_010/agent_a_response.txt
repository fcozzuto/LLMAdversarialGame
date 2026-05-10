def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role)
    if not is_pursuer and (("pursuer" in opponent_role) or ("pursuit" in opponent_role)):
        is_pursuer = False
    if "evader" in self_role:
        is_pursuer = False

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    best_move = (0, 0)
    best_score = None

    def score_cell(nx, ny):
        dist = abs(nx - ox) + abs(ny - oy)
        safe = min(nx, w - 1 - nx, ny, h - 1 - ny)  # higher is safer
        diag = 1 if (nx != sx and ny != sy) else 0
        # small preference for moving when possible
        moved = 1 if (nx != sx or ny != sy) else 0
        if is_pursuer:
            # maximize: closer is better => use negative dist
            return (-dist, safe, diag, moved)
        else:
            # evader: maximize distance
            return (dist, safe, diag, moved)

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                sc = score_cell(nx, ny)
                if best_score is None or sc > best_score:
                    best_score = sc
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]