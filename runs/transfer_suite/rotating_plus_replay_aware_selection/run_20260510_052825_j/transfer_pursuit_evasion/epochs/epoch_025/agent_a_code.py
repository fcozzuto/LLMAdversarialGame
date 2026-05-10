def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if ("evad" in self_role) or (self_role == "evader"):
        mode = "evade"
    elif ("purs" in self_role) or (self_role == "pursuer"):
        mode = "pursue"
    else:
        mode = "pursue" if ("evad" in opponent_role) or (opponent_role == "evader") else "evade"

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs

    # Fixed tie-break ordering to stay deterministic
    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    # Prefer moving toward/away from opponent, then toward a good corner (helps corner evasion)
    corners = [(0, 0), (0, h-1), (w-1, 0), (w-1, h-1)]

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = max(abs(nx - ox), abs(ny - oy))  # capture radius 0 => exact adjacency/position matters via distance
        if mode == "pursue":
            # Primary: minimize distance to opponent
            score = (-dist, nx, ny)
        else:
            # Primary: maximize distance to opponent
            # Secondary: move to corner that maximizes distance from opponent
            corner_bias = 0
            for cx, cy in corners:
                corner_bias = max(corner_bias, max(abs(cx - ox), abs(cy - oy)) - max(abs(cx - nx), abs(cy - ny)))
            score = (dist, corner_bias, -nx, -ny)
        if best is None or (score > best_score):
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]