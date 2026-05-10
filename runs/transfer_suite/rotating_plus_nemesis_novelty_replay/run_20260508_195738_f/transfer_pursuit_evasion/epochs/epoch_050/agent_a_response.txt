def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or (("agent" in self_role) and ("purs" in opp_role))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    obs_list = list(obs_set)
    def min_obs_dist2(x, y):
        md = None
        for ax, ay in obs_list:
            d2 = (x - ax) * (x - ax) + (y - ay) * (y - ay)
            if md is None or d2 < md:
                md = d2
        return 0 if md is None else md

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        cheb = max(abs(nx - ox), abs(ny - oy))
        if pursuer:
            # Minimize distance; break ties by moving toward center and slightly away from obstacles.
            center_d2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            val = (-cheb, -center_d2, min_obs_dist2(nx, ny))
        else:
            # Maximize distance; break ties by pushing away from obstacles and toward anti-opponent corner.
            center_d2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            away_corner = (0 if nx < (w - 1) / 2.0 else 1) + (0 if ny < (h - 1) / 2.0 else 1)
            anti = (nx - (w - 1 - ox)) * (nx - (w - 1 - ox)) + (ny - (h - 1 - oy)) * (ny - (h - 1 - oy))
            val = (cheb, min_obs_dist2(nx, ny), -anti, -center_d2, away_corner)
        if best_key is None or val > best_key:
            best_key = val
            best = [dx, dy]

    return best if best is not None else [0, 0]