def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or ("escape" in self_role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # For evader: bias toward the corner farthest from opponent.
    # For pursuer: bias toward the corner closest to opponent (keeps pressure near where evader likes to go).
    if is_evader:
        cx, cy = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    else:
        cx, cy = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Tie-break deterministically by move preference order:
    pref = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    pref_index = {m: i for i, m in enumerate(pref)}

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, cx, cy)
        # Primary objective: distance (evader) or proximity (pursuer).
        if is_evader:
            score = d_opp * 1000 + d_corner * 2
        else:
            score = -d_opp * 1000 - d_corner * 2

        if best is None or score > best_score or (score == best_score and pref_index[(dx, dy)] < pref_index[best]):
            best, best_score = (dx, dy), score

    return [int(best[0]), int(best[1])]