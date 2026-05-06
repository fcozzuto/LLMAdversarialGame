def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Deterministic tie-break: prefer moves with larger (oppt_dist - self_dist) gain; then smaller self distance;
    # then favor progressing toward the best-scoring resource direction; then deterministic lexicographic.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_cell = None  # (score, do, dm, rx, ry)
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            dm = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Encourage winning races: larger (do - dm) is better. Slightly prefer closer cells too.
            score = (do - dm) * 10 - dm
            cand = (score, do, dm, rx, ry)
            if best_cell is None or (cand > best_cell):
                best_cell = cand
        if best_cell is None:
            continue
        score, do, dm, rx, ry = best_cell

        # Additional shaping: avoid moving away from target and avoid getting too close to opponent.
        toward = -man(nx, ny, rx, ry)
        avoid_opp = man(nx, ny, ox, oy)
        shaped = score + toward + (avoid_opp // 3)

        # Deterministic tie-break uses lexicographic on move.
        key = (shaped, -(dm), -man(nx, ny, rx, ry), dx, dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]