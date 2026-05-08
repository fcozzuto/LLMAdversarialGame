def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" in opp_role)  # heuristic from role names
    if ("evad" in self_role) or ("purs" in opp_role):
        pursuer = False

    # Deterministic intercept heuristic: aim beyond opponent away from our position
    tx = ox + (ox - sx)
    ty = oy + (oy - sy)
    if tx < 0: tx = 0
    if tx >= w: tx = w - 1
    if ty < 0: ty = 0
    if ty >= h: ty = h - 1

    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d_tgt = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # Small obstacle/center bias to break ties deterministically
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        d_center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        if pursuer:
            score = (-d_opp, d_tgt, d_center)   # minimize opponent distance first
        else:
            score = (d_opp, -d_tgt, -d_center)  # maximize opponent distance first

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move