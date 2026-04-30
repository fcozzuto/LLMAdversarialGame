def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_adj(x, y):
        c = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (x + ix, y + iy) in obstacles:
                    c += 1
        return c

    res_set = set(resources)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            val = -10**8  # force avoiding obstacles
        else:
            val = 0
            # maximize advantage for the best remaining resource from next position
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                advantage = opd - myd
                # bonus for reaching directly, and for resources near obstacles (likely bottlenecks)
                bonus = 10 if (nx, ny) == (rx, ry) else 0
                mid = abs(rx - cx) + abs(ry - cy)
                center_bonus = -0.05 * mid
                val = max(val, advantage + bonus + 0.15 * obst_adj(rx, ry) + center_bonus)
            # small deterrent for stepping farther from the currently-best resource
            # (approx via comparing to best from current position)
            curr_best = -10**9
            for rx, ry in resources:
                myd = cheb(sx, sy, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                curr_best = max(curr_best, (opd - myd) + (10 if (sx, sy) == (rx, ry) else 0) + 0.15 * obst_adj(rx, ry))
            if val < curr_best - 1:
                val -= 0.5
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move