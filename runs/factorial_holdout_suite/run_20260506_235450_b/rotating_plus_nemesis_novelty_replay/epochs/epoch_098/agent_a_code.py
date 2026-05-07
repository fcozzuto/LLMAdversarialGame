def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        if ox is None or oy is None:
            score = -min(man(nx, ny, r[0], r[1]) for r in resources)
        else:
            score = None
            for r in resources:
                mx_d = man(nx, ny, r[0], r[1])
                op_d = man(ox, oy, r[0], r[1])
                rel = op_d - mx_d
                s = rel * 10 - mx_d
                if score is None or s > score:
                    score = s
            score = score
        key = (-(score if ox is not None else score), dx, dy) if best_score is None else (0, 0, 0)
        # Deterministic comparison: higher score first, then fixed move order (dx,dy).
        cmp_key = (-score, dx, dy)
        if best_score is None or cmp_key < (best_score, best_move[0], best_move[1]):
            best_score = cmp_key[0]
            best_move = [dx, dy]
    return best_move