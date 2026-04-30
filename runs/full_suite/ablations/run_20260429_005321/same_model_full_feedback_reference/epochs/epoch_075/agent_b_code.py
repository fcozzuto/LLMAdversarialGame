def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if not resources:
        # Deterministic fallback: move toward opponent corner; avoid obstacles.
        ax = 1 if ox > sx else (-1 if ox < sx else 0)
        ay = 1 if oy > sy else (-1 if oy < sy else 0)
        for dx, dy in [(ax, ay), (ax, 0), (0, ay), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose a contested target: closer to me, also consider opponent distance.
    best_t = None
    best_tv = 10**30
    for rx, ry in resources:
        tv = d2(sx, sy, rx, ry) + 0.15 * d2(ox, oy, rx, ry)
        if tv < best_tv:
            best_tv = tv
            best_t = (rx, ry)
    tx, ty = best_t

    cur_d = d2(sx, sy, tx, ty)
    best_move = (0, 0)
    best_score = 10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d = d2(nx, ny, tx, ty)
        # Encourage improvement; discourage backing away; slight bias against staying still.
        improve = my_d - cur_d
        stay_pen = 0 if (dx != 0 or dy != 0) else 6
        # Add a small tie-breaker to prefer moving toward the target direction.
        dir_bias = 0
        if dx != 0 or dy != 0:
            dir_bias = -0.01 * (abs(tx - nx) + abs(ty - ny))
        score = my_d + 8 * improve + stay_pen + dir_bias
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]