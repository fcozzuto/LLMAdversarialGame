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
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("agent" in self_role and "purs" in opp_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    best = None
    best_val = None
    for dx, dy in dirs:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = -d2 if pursuer else d2  # pursuer: minimize distance; evader: maximize
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                return [0, 0]
        return [0, 0]
    return [best[0], best[1]]