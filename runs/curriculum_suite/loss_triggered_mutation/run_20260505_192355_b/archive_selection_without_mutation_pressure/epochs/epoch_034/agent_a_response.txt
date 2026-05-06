def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    preferred = [r for r in resources if abs(r[1] - oy) <= 1]
    pool = preferred if preferred else resources

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        local_best = None
        for rx, ry in pool:
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            adv = opd - myd  # positive => we get there no later
            # reward picking resources near opponent's row (denier style), and being competitive
            row_align = 2 if abs(ry - oy) == 0 else 1 if abs(ry - oy) == 1 else 0
            # smaller myd better; obstacles handled by inb
            score = (adv >= 0) * 100000 + row_align * 1000 + adv * 10 - myd
            if local_best is None or score > local_best:
                local_best = score

        # tie-break: choose move with lexicographically smaller delta for determinism
        if best_score is None or local_best > best_score or (local_best == best_score and (dx, dy) < best_move):
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]