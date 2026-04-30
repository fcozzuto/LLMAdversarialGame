def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick a resource that we can get relative to the opponent.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Lower is better: prioritize resources where opponent is farther; also prefer nearer overall.
        priority = (ds - do) * 10 + ds
        key = (priority, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    # Greedy step toward target with obstacle/bounds avoidance.
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                deltas.append((dx, dy))

    # If somehow we're already at target, try to stay unless forced.
    if sx == tx and sy == ty:
        return [0, 0]

    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        dist = man(nx, ny, tx, ty)
        # Tie-break deterministically: prefer smaller dx then dy.
        key = (dist, abs(dx) + abs(dy), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [int(best_move[1]), int(best_move[2])]