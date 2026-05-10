def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1))

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_us = dist8(sx, sy, rx, ry)
            d_op = dist8(ox, oy, rx, ry)
            adv = d_op - d_us  # positive means we are closer
            # Prefer higher advantage, then closer target
            cand = (adv, -d_us, -(abs(rx - ox) + abs(ry - oy)))
            if best is None or cand > best[0]:
                best = (cand, (rx, ry))
        tx, ty = best[1]
        best_move = (-(10**9), 10**9, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            d1 = dist8(nx, ny, tx, ty)
            d_us2 = d1
            d_op2 = dist8(ox, oy, tx, ty)
            # Primary: minimize distance to target; Secondary: maximize current advantage; Tertiary: keep away from opponent
            adv2 = d_op2 - d_us2
            away = dist8(nx, ny, ox, oy)
            cand = (adv2, -d1, -away, dx, dy)
            if cand > best_move:
                best_move = cand
        return [best_move[3], best_move[4]]
    else:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            d_center = dist8(nx, ny, cx, cy)
            d_opp = dist8(nx, ny, ox, oy)
            cand = (-d_center, d_opp)
            if best is None or cand > best[0]:
                best = (cand, (dx, dy))
        return [best[1][0], best[1][1]]