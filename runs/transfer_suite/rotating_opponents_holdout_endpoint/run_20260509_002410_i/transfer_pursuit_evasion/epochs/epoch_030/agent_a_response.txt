def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    sr = (observation.get("self_role") or "").lower()
    orr = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in sr) or ("purs" in orr and "evad" not in sr)
    self_is_evader = ("evad" in sr) or ("evad" in orr and "purs" not in sr)
    if not (self_is_pursuer or self_is_evader):
        self_is_pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy)) if self_is_evader else min(corners, key=lambda c: man(c[0], c[1], ox, oy))

    best = None
    if self_is_evader:
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            d_corner = man(nx, ny, target_corner[0], target_corner[1])
            wall_penalty = 0
            if nx == sx and ny == sy:
                wall_penalty = -1
            val = 10 * d_opp + 2 * d_corner + wall_penalty
            if (best is None) or (val > best_val) or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)
    else:
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            toward = -d_opp
            d_corner = -man(nx, ny, target_corner[0], target_corner[1])
            val = 10 * toward + 1 * d_corner
            if (best is None) or (val > best_val) or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]