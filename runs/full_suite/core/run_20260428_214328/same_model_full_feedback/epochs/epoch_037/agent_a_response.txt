def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate best move by minimizing our distance while maximizing our advantage over opponent.
    best = None
    best_score = -10**18
    # Deterministic tie-breaker order by dirs list index.
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Choose the resource that gives best combined objective from this next position.
        local_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Encourage taking resources and gaining distance advantage.
            # If equal distance, prefer the one closer to us next step (lower sd).
            score = (-2.0 * sd) + (1.6 * (od - sd))
            # Slight bias toward closer resources overall to reduce dithering.
            score += -0.05 * (sd + od)
            if score > local_best:
                local_best = score
        # Add a small preference to move along x then y deterministically to stabilize.
        stab = -0.01 * (abs(nx - sx) * 100 + abs(ny - sy))
        total = local_best + stab
        if total > best_score:
            best_score = total
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]