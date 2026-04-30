def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def move_bad(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in occ:
                pen += 30
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in occ:
                pen += 10
        # If opponent is very close, avoid giving them an easy capture path.
        d = manh(x, y, ox, oy)
        if d <= 1:
            pen += 60
        elif d == 2:
            pen += 20
        return pen

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in occ:
            continue

        our_score = -move_bad(nx, ny)
        # Deterministic target evaluation: pick resources where we are relatively closer than opponent.
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            od = manh(ox, oy, rx, ry)
            nd = manh(nx, ny, rx, ry)

            # Advantage term: large reward if we are closer (or will likely arrive sooner).
            adv = od - nd
            if adv >= 0:
                s = 200 * adv - nd
            else:
                s = 15 * adv - 2 * nd  # still move toward if no advantage exists

            # Block-like effect: prioritize resources near where opponent already is.
            # (If opponent is close, denying by approaching that region helps.)
            if manh(ox, oy, rx, ry) <= 3:
                s += 40

            if s > local_best:
                local_best = s

        our_score += local_best

        # Small tie-break: prefer moves that reduce distance to the closest "advantage" resource.
        # Deterministic because resources order is fixed by observation.
        if our_score > best_score:
            best_score = our_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]