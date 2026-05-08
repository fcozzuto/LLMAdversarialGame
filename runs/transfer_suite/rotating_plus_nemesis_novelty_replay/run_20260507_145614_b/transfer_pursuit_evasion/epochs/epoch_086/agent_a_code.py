def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role) or ("hunter" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(x, y):
        return (0 if x < 0 else (w - 1 if x >= w else x),
                0 if y < 0 else (h - 1 if y >= h else y))

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_score(x, y):
        if (x, y) in obst:
            return -10**9
        if not obst:
            return 0.0
        best = 10**18
        for bx, by in obst:
            d = dist2(x, y, bx, by)
            if d < best:
                best = d
        if best <= 1:
            return -200.0
        return 20.0 / (1.0 + best)

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obst and (nx, ny) != (sx, sy):
            continue
        d = dist2(nx, ny, ox, oy)
        # Deterministic tie-breaker uses move order and coordinate sums
        if is_pursuer:
            score = -d + 0.5 * obstacle_score(nx, ny)
        else:
            score = d + 0.8 * obstacle_score(nx, ny)
            # Prefer escaping toward farthest corner-ish (helps evasion_corner)
            score += 0.05 * max(dist2(nx, ny, 0, 0), dist2(nx, ny, w - 1, 0), dist2(nx, ny, 0, h - 1), dist2(nx, ny, w - 1, h - 1))
        key = (score, -abs(dx) - abs(dy), -(nx + ny))
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]