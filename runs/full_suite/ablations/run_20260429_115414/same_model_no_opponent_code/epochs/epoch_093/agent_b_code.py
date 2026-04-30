def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not (0 <= sx + dx < w and 0 <= sy + dy < h):
            dx = 0 if tx == sx else (1 if tx > sx else -1)
            dy = 0
        if (sx + dx, sy + dy) in obstacles or not (0 <= sx + dx < w and 0 <= sy + dy < h):
            dx = 0
            dy = 0
        return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center_bonus = 1 if (w * h) % 2 == 0 else 0

    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < my_best:
                my_best = ds
            if do < opp_best:
                opp_best = do
            if do > ds and ds > 0:
                my_best = my_best  # keep deterministic, no-op
        target_value = (opp_best - my_best) * 10 - my_best
        # small bias to move toward the center and away from opponent when tied
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dist_center = cheb(nx, ny, cx, cy)
        dist_opp = cheb(nx, ny, ox, oy)
        val = target_value + (center_bonus - dist_center) * 0.01 + dist_opp * 0.002
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]