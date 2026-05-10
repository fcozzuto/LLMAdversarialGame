def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in sr) or ("catch" in sr) or ("hunt" in sr) or ("pursuer" in sr) or ("chaser" in sr)
    if not self_is_pursuer and ("purs" in pr or "catch" in pr or "hunt" in pr or "pursuer" in pr or "chaser" in pr):
        self_is_pursuer = False
    self_is_evader = not self_is_pursuer

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if self_is_evader:
            val = dist2
        else:
            val = -dist2
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best_move