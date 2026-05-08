def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = observation.get("self_role") or ""
    is_pursuer = "purs" in self_role.lower()

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) in obs:
        obs.discard((sx, sy))

    def cheb(x, y):
        dx, dy = x - ox, y - oy
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def obst_gap(x, y):
        if not obs:
            return 99
        best = 99
        for (px, py) in obs:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        return best

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy)) if not is_pursuer else min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d = cheb(nx, ny)
        gap = obst_gap(nx, ny)
        corner_dist = abs(nx - target_corner[0]) + abs(ny - target_corner[1])

        if is_pursuer:
            score = (-d, corner_dist, -gap, nx, ny)  # drive to opponent; avoid obstacles
        else:
            score = (d, -corner_dist, gap, -nx, -ny)  # run away; drift to safe corner

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move != [0, 0] else [0, 0]