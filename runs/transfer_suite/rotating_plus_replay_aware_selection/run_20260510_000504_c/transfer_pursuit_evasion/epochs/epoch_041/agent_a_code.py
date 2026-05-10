def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs if p is not None and len(p) >= 2)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = any(k in self_role for k in ("purs", "chase", "hunter"))
    if not i_am_pursuer:
        if any(k in opp_role for k in ("purs", "chase", "hunter")):
            i_am_pursuer = False
        else:
            i_am_pursuer = ("evad" not in self_role) and ("escap" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dx_pref = 1 if ox > sx else -1 if ox < sx else 0
    dy_pref = 1 if oy > sy else -1 if oy < sy else 0

    def d2(nx, ny):
        dx = nx - ox
        dy = ny - oy
        return dx * dx + dy * dy

    want = 1 if i_am_pursuer else -1
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = want * d2(nx, ny)
        score += 0.01 * (dx * dx_pref + dy * dy_pref)  # tiny deterministic bias
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best