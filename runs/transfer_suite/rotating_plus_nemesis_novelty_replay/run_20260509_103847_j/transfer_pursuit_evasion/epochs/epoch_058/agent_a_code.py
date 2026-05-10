def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obs_set = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    self_evader = ("evader" in sr) or ("evade" in sr) or ("escape" in sr)
    opp_pursuer = ("purs" in pr) or ("chaser" in pr) or ("catch" in pr) or ("hunt" in pr)
    pursue_mode = (not self_evader) or opp_pursuer

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    tx, ty = ox, oy
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        val = -d2 if pursue_mode is False else d2
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]