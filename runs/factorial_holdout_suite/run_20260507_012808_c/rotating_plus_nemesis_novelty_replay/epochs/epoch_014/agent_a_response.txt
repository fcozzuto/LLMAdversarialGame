def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)
        best = (10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist((nx, ny), (tx, ty))
            if d < best[0]:
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    best_target = resources[0]
    best_val = 10**9
    for rx, ry in resources:
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        val = (d1 - 0.85 * d2) + 0.03 * (abs(rx - sx) + abs(ry - sy))
        if val < best_val:
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist((nx, ny), (rx, ry))
        d_op = dist((nx, ny), (ox, oy))
        score = d - 0.06 * d_op  # keep some distance from denier while heading in
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]