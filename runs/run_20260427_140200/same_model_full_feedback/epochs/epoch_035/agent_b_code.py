def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Go toward center while keeping deterministic obstacle-avoidance
        tx, ty = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = dist(nx, ny, tx, ty)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    # Pick target resource likely reachable earlier than opponent (deterministic tie-break).
    best_r = None
    best_score = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Lower is better: prefer resources we are relatively closer to, with slight bias away from opponent.
        score = ds - 0.78 * do
        if best_score is None or score < best_score or (score == best_score and (rx, ry) < best_r):
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r
    # Evaluate immediate moves: progress to target, plus "beat opponent" potential.
    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = dist(nx, ny, tx, ty)

        beat = 0
        # Small deterministic look: count how many resources we'd be closer to than opponent.
        for rx, ry in resources:
            if dist(nx, ny, rx, ry) < dist(ox, oy, rx, ry):
                beat += 1

        # Also add tie-breaker to avoid feeding opponent by moving closer to them when equal.
        d_op = dist(nx, ny, ox, oy)
        val = (d_to_t, -beat, d_op, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])] if best_move is not None else [0, 0]