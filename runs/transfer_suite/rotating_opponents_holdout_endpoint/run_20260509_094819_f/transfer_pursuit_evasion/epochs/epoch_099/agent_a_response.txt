def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    evader = ("evader" in sr) or ("escape" in sr) or ("runner" in sr) or ("evasion" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        if (nx, ny) in blocked:
            return -10**9
        d = cheb(nx, ny, ox, oy)
        near_obs = 0
        if blocked:
            for (bx, by) in blocked:
                if cheb(nx, ny, bx, by) <= 1:
                    near_obs += 1
        center_bias = -abs(nx - (w - 1) / 2.0) * 0.01 - abs(ny - (h - 1) / 2.0) * 0.01
        if evader:
            return d * 10.0 - near_obs * 2.0 + center_bias
        else:
            return -d * 10.0 - near_obs * 2.0 + center_bias

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        sc = score_move(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]