def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Score candidate resource: prefer arriving earlier with large lead; otherwise deny by being the closest.
    best_target = None
    best_score = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        lead = do - ds  # positive: we are closer
        if ds <= do:
            score = lead * 1000 - ds
        else:
            score = -ds - do * 2 + (lead) * 5
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target

    # Choose best immediate move toward target, avoiding obstacles, maximizing (opponent-distance - self-distance).
    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    moves.sort()  # deterministic tie-break
    best_move = (0, 0)
    best_ms = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = md(nx, ny, tx, ty)
        # immediate tactical objective: closer to target and widen lead at that target
        do2 = md(ox, oy, tx, ty)
        lead2 = do2 - ds2
        val = lead2 * 10 - ds2
        # small preference for staying unblocked/centering toward increasing progress
        prog = -ds2
        total = val * 100 + prog
        if best_ms is None or total > best_ms:
            best_ms = total
            best_move = (dx, dy)

    # If all moves invalid (surrounded by obstacles), stay.
    if best_ms is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]