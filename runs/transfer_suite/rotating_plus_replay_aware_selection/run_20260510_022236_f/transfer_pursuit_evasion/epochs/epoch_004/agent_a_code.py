def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            ax, ay = int(p[0]), int(p[1])
        except Exception:
            continue
        if 0 <= ax < w and 0 <= ay < h:
            obs.add((ax, ay))

    role = (observation.get("self_role", "") or "").lower()
    evade = ("evad" in role) and ("purs" not in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    target = corners[phase]
    if evade:
        best_corner = target
        best_corner_dist = -1
        for c in corners:
            cx, cy = c
            d = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
            if d > best_corner_dist:
                best_corner_dist = d
                best_corner = c
        target = best_corner

    # Primary objective: adjust distance to opponent (pursuit/evasion)
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ddx, ddy = nx - ox, ny - oy
            d2 = ddx * ddx + ddy * ddy
            # Tie-breakers are deterministic: prefer moving away/towards target corner for evader
            if evade:
                corner_d2 = (nx - target[0]) * (nx - target[0]) + (ny - target[1]) * (ny - target[1])
                score = (d2, corner_d2, -dx, -dy)
            else:
                score = (-d2, -(nx - target[0]) * (nx - target[0]) - (ny - target[1]) * (ny - target[1]), -dx, -dy)

            if best_score is None:
                best_score = score
                best_move = [dx, dy]
            else:
                if score > best_score:
                    best_score = score
                    best_move = [dx, dy]

    # If all moves blocked, stay
    if not ok(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]