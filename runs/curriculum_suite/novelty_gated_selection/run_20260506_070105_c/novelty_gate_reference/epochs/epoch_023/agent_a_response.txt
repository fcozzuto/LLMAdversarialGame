def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
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

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    def d(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Strategic shift: prioritize resources on/near opponent's sweep band (same y),
    # and choose a move that maximizes our "winning margin" after the step.
    best = None
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        step_best = -10**18
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in blocked:
                continue
            self_dist = d(nx, ny, rx, ry)
            opp_dist = d(ox, oy, rx, ry)

            # Prefer being close to opponent's current row (interception with sweep_rows archetype).
            band = abs(ry - oy)
            # Winning margin: we want ourselves closer than opponent, but also avoid too slow routes.
            # Tie-breakers: prefer lower band, then smaller self distance.
            score = (-self_dist + 0.9 * opp_dist) - 0.25 * band - 0.01 * self_dist
            if score > step_best:
                step_best = score
        if step_best > best_score:
            best_score = step_best
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best