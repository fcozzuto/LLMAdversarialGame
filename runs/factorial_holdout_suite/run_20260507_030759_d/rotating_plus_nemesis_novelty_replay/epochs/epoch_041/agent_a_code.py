def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**18

    # If resources exist, decide by "can I arrive first here?" plus "how much closer am I?"
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            self_d_best = 10**9
            opp_d_best = 10**9
            win_margin = -10**9
            for rx, ry in resources:
                dself = dist((nx, ny), (rx, ry))
                doppel = dist((ox, oy), (rx, ry))
                if dself < self_d_best:
                    self_d_best = dself
                if doppel < opp_d_best:
                    opp_d_best = doppel
                m = doppel - dself
                if m > win_margin:
                    win_margin = m
            # Prefer immediate captures (d=0), then largest arrival advantage (win_margin)
            # then closeness improvement (lower self_d_best), with slight anti-stall.
            score = 1000000 * win_margin - 10 * self_d_best + (1 if (nx == sx and ny == sy) else 0) * -1
            # Small preference to reduce distance to opponent when tied (prevents easy grabs)
            score += 0.5 * (dist((nx, ny), (ox, oy)) * -1)
            # Deterministic tie-break: lexical preference on move order (already fixed)
            if score > best_score:
                best_score = score
                best = [dx, dy]
    else:
        # No visible resources: drift to center to reduce time-to-contact deterministically
        target_x = (w - 1) // 2
        target_y = (h - 1) // 2
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d_to_center = dist((nx, ny), (target_x, target_y))
            # Prefer moves that decrease distance; avoid staying if equal
            score = -d_to_center + (0 if (nx == sx and ny == sy) else 0.01)
            if score > best_score:
                best_score = score
                best = [dx, dy]

    return [int(best[0]), int(best[1])]