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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target_x = 0 if ox > (w - 1) / 2.0 else (w - 1)
    target_y = 0 if oy > (h - 1) / 2.0 else (h - 1)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in blocked:
            v = -10**9 if evader else -10**9
        else:
            d_opp = cheb(nx, ny, ox, oy)
            d_tgt = cheb(nx, ny, target_x, target_y)
            near_obs = 0
            for bx, by in blocked:
                if cheb(nx, ny, bx, by) <= 1:
                    near_obs += 1
            center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.01
            obstacle_pen = near_obs * 2.5

            if evader:
                # Maximize distance from pursuer; also drift toward far corner.
                v = d_opp * 10.0 + d_tgt * 0.8 + center_bias - obstacle_pen
            else:
                # Minimize distance to pursuer; also avoid dead-end proximity to obstacles.
                v = -d_opp * 10.0 - d_tgt * 0.3 + center_bias - obstacle_pen

        if best is None or (v > bestv) or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]