def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    self_score = 0
    opp_score = 0
    sc = observation.get("scores")
    if isinstance(sc, (list, tuple)) and len(sc) >= 2:
        self_score, opp_score = sc[0], sc[1]
    elif isinstance(sc, dict):
        self_score = sc.get("self", sc.get("player", 0)) or 0
        opp_score = sc.get("opponent", sc.get("enemy", 0)) or 0

    if self_score >= opp_score:
        tx, ty = cx, cy
    else:
        tx, ty = (cx + 2*(cx - ox)), (cy + 2*(cy - oy))

    best = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer reducing distance to target, while also increasing distance from opponent if behind.
        dtx = abs(nx - tx) + abs(ny - ty)
        dco = abs(nx - ox) + abs(ny - oy)
        val = (dtx, -dco) if self_score >= opp_score else (dtx, dco)
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]
    return best