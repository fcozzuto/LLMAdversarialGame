def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if resources:
        best = None
        for rx, ry in resources:
            ds = cd(sx, sy, rx, ry)
            do = cd(ox, oy, rx, ry)
            rel = (do - ds)  # positive => we are closer
            # If opponent is closer, heavily penalize to contest/block later
            val = ds + (0 if rel > 0 else 6 + (-rel))
            # Small deterministic tie-breakers
            val = val * 1000 + (rx * 8 + ry)
            if best is None or val < best[0]:
                best = (val, rx, ry)
        _, tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    cur_do = cd(ox, oy, tx, ty)
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d1 = cd(nx, ny, tx, ty)
        d2 = cd(ox, oy, tx, ty)  # opponent unchanged this turn
        # If we can reach target sooner than opponent would, prioritize that
        reach_bonus = 0
        if d1 <= d2:
            reach_bonus = 3
        score = d1 * 10 - reach_bonus
        # Avoid moving closer to opponent when no resources
        if not resources:
            score += cd(nx, ny, ox, oy)
        if score < best_move[0] or (score == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (score, dx, dy)

    return [int(best_move[1]), int(best_move[2])]