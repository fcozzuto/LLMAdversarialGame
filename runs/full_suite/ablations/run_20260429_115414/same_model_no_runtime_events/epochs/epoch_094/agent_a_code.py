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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
    else:
        best = resources[0]
        best_val = -10**18
        mx, my = (w - 1) / 2.0, (h - 1) / 2.0
        for rx, ry in resources:
            us = cheb(sx, sy, rx, ry)
            them = cheb(ox, oy, rx, ry)
            center = - (abs(rx - mx) + abs(ry - my)) * 0.01
            val = (them - us) * 1000 - us + center
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        usd = cheb(nx, ny, tx, ty)
        thd = cheb(ox, oy, tx, ty)
        # Prefer reducing distance to target; if equal, prefer increasing opponent distance to target.
        score = -usd * 1000 + (thd - cheb(nx, ny, ox, oy)) * 5
        # Also nudge toward nearer to target overall deterministically.
        score += -cheb(nx, ny, (tx + ox) // 2, (ty + oy) // 2) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]