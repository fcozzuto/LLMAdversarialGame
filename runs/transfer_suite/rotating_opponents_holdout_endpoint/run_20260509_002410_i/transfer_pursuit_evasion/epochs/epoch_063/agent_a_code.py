def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("flee" in role) or ("run" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def free_legal(x, y):
        return inside(x, y) and not blocked(x, y)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free_legal(nx, ny):
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free_legal(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        mob = mobility(nx, ny)

        # Heuristic:
        # Evader: maximize (dist, mobility), avoid stepping into tight cells.
        # Pursuer: minimize (dist), then maximize mobility to keep pressure.
        if is_evader:
            score = (dist2, mob, -(abs(nx - (w - 1 if ox < w // 2 else 0)) + abs(ny - (h - 1 if oy < h // 2 else 0))))
            better = best is None or score > best_score
        else:
            score = (-dist2, mob, abs(nx - ox) + abs(ny - oy))
            better = best is None or score > best_score

        if better:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]