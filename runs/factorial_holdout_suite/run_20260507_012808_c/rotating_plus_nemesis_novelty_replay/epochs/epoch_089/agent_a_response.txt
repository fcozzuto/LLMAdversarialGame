def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = (w - 1, h - 1) if (sx + sy) < (w // 2 + h // 2) else (0, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    resources.sort()
    best = resources[0]
    best_key = None
    for rx, ry in resources:
        d1 = manh(sx, sy, rx, ry)
        d2 = manh(ox, oy, rx, ry)
        # prefer: (self sooner), (opponent later), then smaller distance, then lexicographic
        key = (d1 - d2, d1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    step_candidates = [
        (0, 0),
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1),
    ]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # score candidate by progress to target, but avoid getting stuck
    best_move = (0, 0)
    best_move_score = None
    for dx, dy in step_candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dn = manh(nx, ny, tx, ty)
        on = manh(ox, oy, tx, ty)
        # prefer minimizing self distance, also slightly pushing away from opponent if they are close
        score = (dn, dn - on, abs(dx) + abs(dy))
        if best_move_score is None or score < best_move_score:
            best_move_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]